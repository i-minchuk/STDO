import { useEffect, useState } from 'react';
import { Bell, X } from 'lucide-react';
import { getNotifications, markNotificationRead, getUnreadNotificationCount } from '../api/gamification';
import type { Notification } from '../types';

interface NotificationBellProps {
  onNotificationClick?: () => void;
  className?: string;
}

export default function NotificationBell({ onNotificationClick, className = '' }: NotificationBellProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadNotifications();
    const interval = setInterval(loadUnreadCount, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    try {
      const data = await getNotifications();
      setNotifications(data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const data = await getUnreadNotificationCount();
      setUnreadCount(data.count);
    } catch (error) {
      console.error('Failed to load unread count:', error);
    }
  };

  const handleMarkAsRead = async (notificationId: number) => {
    try {
      await markNotificationRead(notificationId);
      setNotifications(prev =>
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const unreadNotifications = notifications.filter(n => !n.is_read);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`relative p-2 rounded-lg transition-all ${className}`}
        style={{ color: 'var(--notification-icon, var(--text-tertiary))' }}
      >
        <Bell size={20} className="w-5 h-5" />
        {unreadCount > 0 && (
          <span 
            className="absolute -top-0.5 -right-0.5 text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium shadow-sm"
            style={{ 
              backgroundColor: 'var(--notification-badge, #EF4444)',
              color: '#FFFFFF'
            }}
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div 
            className="absolute right-0 mt-2 w-80 rounded-lg shadow-lg border z-50"
            style={{ 
              backgroundColor: 'var(--bg-surface)',
              borderColor: 'var(--border-default)'
            }}
          >
            <div className="p-4 border-b" style={{ borderColor: 'var(--border-default)' }}>
              <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Уведомления</h3>
            </div>

            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-4 text-center" style={{ color: 'var(--text-tertiary)' }}>
                  Нет уведомлений
                </div>
              ) : (
                notifications.slice(0, 10).map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-4 border-b hover:bg-[var(--bg-hover)] cursor-pointer transition-colors ${
                      !notification.is_read ? '' : ''
                    }`}
                    style={{ 
                      borderColor: 'var(--border-light)',
                      backgroundColor: !notification.is_read ? 'var(--primary-light)' : 'transparent'
                    }}
                    onClick={() => !notification.is_read && handleMarkAsRead(notification.id)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                          {notification.title}
                        </h4>
                        <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                          {notification.message}
                        </p>
                        <p className="text-xs mt-2" style={{ color: 'var(--text-tertiary)' }}>
                          {new Date(notification.created_at).toLocaleString('ru-RU')}
                        </p>
                      </div>
                      {!notification.is_read && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMarkAsRead(notification.id);
                          }}
                          className="ml-2 hover:text-[var(--text-primary)] transition-colors"
                          style={{ color: 'var(--text-tertiary)' }}
                        >
                          <X size={14} />
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            {notifications.length > 10 && (
              <div className="p-3 border-t text-center" style={{ borderColor: 'var(--border-default)' }}>
                <button
                  onClick={onNotificationClick}
                  className="text-sm font-medium transition-colors"
                  style={{ color: 'var(--primary)', '--tw-text-opacity': 1 }}
                >
                  Посмотреть все уведомления
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}