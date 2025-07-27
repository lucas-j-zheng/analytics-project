from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_jwt_extended import decode_token
from datetime import datetime
import json

# Real-time collaboration service
class CollaborationService:
    def __init__(self, socketio, db):
        self.socketio = socketio
        self.db = db
        self.active_sessions = {}  # Store active collaboration sessions
        self.user_rooms = {}  # Track which rooms users are in
        
    def init_events(self):
        @self.socketio.on('connect')
        def handle_connect(auth):
            try:
                # Verify JWT token from auth
                if not auth or 'token' not in auth:
                    disconnect()
                    return False
                
                # Decode token to get user info
                token_data = decode_token(auth['token'])
                user_id = token_data['sub']
                user_type = token_data.get('user_type', 'team')
                
                # Store user session
                request.sid_user = {
                    'id': user_id,
                    'type': user_type,
                    'sid': request.sid
                }
                
                emit('connected', {'status': 'success', 'user_id': user_id})
                
            except Exception as e:
                print(f"Connection error: {e}")
                disconnect()
                return False
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            if hasattr(request, 'sid_user'):
                user_info = request.sid_user
                # Leave all rooms
                for room in list(self.user_rooms.get(user_info['id'], [])):
                    self.leave_collaboration_room(room, user_info)
        
        @self.socketio.on('join_collaboration')
        def handle_join_collaboration(data):
            if not hasattr(request, 'sid_user'):
                return
                
            user_info = request.sid_user
            room_id = data.get('room_id')
            room_type = data.get('type', 'chart')  # chart, game, team
            
            if not room_id:
                emit('error', {'message': 'Room ID required'})
                return
            
            self.join_collaboration_room(room_id, room_type, user_info)
        
        @self.socketio.on('leave_collaboration')
        def handle_leave_collaboration(data):
            if not hasattr(request, 'sid_user'):
                return
                
            user_info = request.sid_user
            room_id = data.get('room_id')
            
            if room_id:
                self.leave_collaboration_room(room_id, user_info)
        
        @self.socketio.on('chart_update')
        def handle_chart_update(data):
            if not hasattr(request, 'sid_user'):
                return
                
            user_info = request.sid_user
            room_id = data.get('room_id')
            changes = data.get('changes', {})
            
            if not room_id:
                return
            
            # Broadcast chart changes to all users in the room except sender
            self.socketio.emit('chart_updated', {
                'room_id': room_id,
                'changes': changes,
                'updated_by': {
                    'id': user_info['id'],
                    'type': user_info['type']
                },
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_id, include_self=False)
        
        @self.socketio.on('cursor_position')
        def handle_cursor_position(data):
            if not hasattr(request, 'sid_user'):
                return
                
            user_info = request.sid_user
            room_id = data.get('room_id')
            position = data.get('position', {})
            
            if not room_id:
                return
            
            # Broadcast cursor position to others in room
            self.socketio.emit('cursor_moved', {
                'user_id': user_info['id'],
                'user_type': user_info['type'],
                'position': position,
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_id, include_self=False)
        
        @self.socketio.on('typing_indicator')
        def handle_typing(data):
            if not hasattr(request, 'sid_user'):
                return
                
            user_info = request.sid_user
            room_id = data.get('room_id')
            is_typing = data.get('is_typing', False)
            field = data.get('field', 'general')
            
            if not room_id:
                return
            
            # Broadcast typing indicator
            self.socketio.emit('user_typing', {
                'user_id': user_info['id'],
                'user_type': user_info['type'],
                'is_typing': is_typing,
                'field': field,
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_id, include_self=False)
        
        @self.socketio.on('notification')
        def handle_notification(data):
            if not hasattr(request, 'sid_user'):
                return
                
            user_info = request.sid_user
            target_user_id = data.get('target_user_id')
            notification_type = data.get('type', 'general')
            message = data.get('message', '')
            
            if not target_user_id:
                return
            
            # Send notification to specific user
            self.send_notification(target_user_id, {
                'type': notification_type,
                'message': message,
                'from_user': {
                    'id': user_info['id'],
                    'type': user_info['type']
                },
                'timestamp': datetime.utcnow().isoformat()
            })
    
    def join_collaboration_room(self, room_id, room_type, user_info):
        join_room(room_id)
        
        # Track user in room
        if user_info['id'] not in self.user_rooms:
            self.user_rooms[user_info['id']] = set()
        self.user_rooms[user_info['id']].add(room_id)
        
        # Initialize session if not exists
        if room_id not in self.active_sessions:
            self.active_sessions[room_id] = {
                'type': room_type,
                'users': {},
                'created_at': datetime.utcnow().isoformat()
            }
        
        # Add user to session
        self.active_sessions[room_id]['users'][user_info['id']] = {
            'type': user_info['type'],
            'joined_at': datetime.utcnow().isoformat(),
            'sid': request.sid
        }
        
        # Notify others that user joined
        self.socketio.emit('user_joined', {
            'user_id': user_info['id'],
            'user_type': user_info['type'],
            'room_id': room_id,
            'active_users': list(self.active_sessions[room_id]['users'].keys())
        }, room=room_id, include_self=False)
        
        # Send current session info to the joining user
        emit('collaboration_joined', {
            'room_id': room_id,
            'room_type': room_type,
            'active_users': list(self.active_sessions[room_id]['users'].keys()),
            'session_info': self.active_sessions[room_id]
        })
    
    def leave_collaboration_room(self, room_id, user_info):
        leave_room(room_id)
        
        # Remove from tracking
        if user_info['id'] in self.user_rooms:
            self.user_rooms[user_info['id']].discard(room_id)
        
        # Remove from session
        if room_id in self.active_sessions and user_info['id'] in self.active_sessions[room_id]['users']:
            del self.active_sessions[room_id]['users'][user_info['id']]
            
            # Notify others that user left
            self.socketio.emit('user_left', {
                'user_id': user_info['id'],
                'user_type': user_info['type'],
                'room_id': room_id,
                'active_users': list(self.active_sessions[room_id]['users'].keys())
            }, room=room_id)
            
            # Clean up empty sessions
            if not self.active_sessions[room_id]['users']:
                del self.active_sessions[room_id]
    
    def send_notification(self, user_id, notification_data):
        """Send notification to specific user across all their sessions"""
        for room_id, session in self.active_sessions.items():
            if user_id in session['users']:
                user_sid = session['users'][user_id]['sid']
                self.socketio.emit('notification_received', notification_data, room=user_sid)
                break
    
    def broadcast_to_team(self, team_id, event_name, data):
        """Broadcast event to all users of a specific team"""
        room_id = f"team_{team_id}"
        self.socketio.emit(event_name, data, room=room_id)
    
    def get_active_sessions(self):
        """Get all active collaboration sessions"""
        return {
            'sessions': self.active_sessions,
            'total_sessions': len(self.active_sessions),
            'total_users': sum(len(session['users']) for session in self.active_sessions.values())
        }