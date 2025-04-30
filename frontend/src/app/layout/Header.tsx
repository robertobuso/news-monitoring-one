import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../providers/AuthProvider';
import { 
  UserCircleIcon, 
  BellIcon, 
  ChevronDownIcon 
} from '@heroicons/react/24/outline';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement>(null);

  const toggleProfileMenu = () => {
    setIsProfileMenuOpen(!isProfileMenuOpen);
  };

  // Close the profile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
        setIsProfileMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <header className="bg-white shadow-sm z-10">
      <div className="flex justify-between items-center px-4 py-3">
        <div className="flex-1">
          <h1 className="text-xl font-semibold text-gray-800 md:block hidden">
            {window.location.pathname.includes('/dashboard') && 'Dashboard'}
            {window.location.pathname.includes('/clients') && 'Client Profiles'}
            {window.location.pathname.includes('/feeds') && 'News Feeds'}
            {window.location.pathname.includes('/articles') && 'Articles'}
            {window.location.pathname.includes('/reports') && 'Reports'}
          </h1>
        </div>
        
        <div className="flex items-center space-x-4">
          <button className="p-1 rounded-full text-gray-500 hover:text-gray-700 focus:outline-none">
            <BellIcon className="h-6 w-6" />
          </button>
          
          <div className="relative" ref={profileMenuRef}>
            <button
              onClick={toggleProfileMenu}
              className="flex items-center text-sm rounded-full focus:outline-none"
            >
              <UserCircleIcon className="h-8 w-8 text-gray-500" />
              <span className="ml-2 text-gray-700 hidden md:block">
                {user?.first_name} {user?.last_name}
              </span>
              <ChevronDownIcon className="ml-1 h-4 w-4 text-gray-500 hidden md:block" />
            </button>
            
            {isProfileMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                <div className="px-4 py-2 text-sm text-gray-700 border-b">
                  <div className="font-medium">{user?.first_name} {user?.last_name}</div>
                  <div className="text-gray-500 truncate">{user?.email}</div>
                </div>
                <a
                  href="#profile"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Your Profile
                </a>
                <a
                  href="#settings"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Settings
                </a>
                <button
                  onClick={logout}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;