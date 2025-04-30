import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  UsersIcon, 
  RssIcon, 
  NewspaperIcon, 
  DocumentTextIcon,
  XMarkIcon,
  Bars3Icon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface NavItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
  active: boolean;
}

const NavItem: React.FC<NavItemProps> = ({ to, icon, label, active }) => (
  <Link
    to={to}
    className={clsx(
      'flex items-center px-4 py-3 text-sm font-medium rounded-md transition-colors',
      active
        ? 'bg-blue-700 text-white'
        : 'text-gray-300 hover:bg-blue-800 hover:text-white'
    )}
  >
    <span className="mr-3 h-5 w-5">{icon}</span>
    <span>{label}</span>
  </Link>
);

const Sidebar: React.FC = () => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navItems = [
    { to: '/dashboard', icon: <HomeIcon />, label: 'Dashboard' },
    { to: '/clients', icon: <UsersIcon />, label: 'Clients' },
    { to: '/feeds', icon: <RssIcon />, label: 'News Feeds' },
    { to: '/articles', icon: <NewspaperIcon />, label: 'Articles' },
    { to: '/reports', icon: <DocumentTextIcon />, label: 'Reports' },
  ];

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <>
      {/* Mobile menu button */}
      <div className="fixed top-0 left-0 z-40 m-4 md:hidden">
        <button
          onClick={toggleMobileMenu}
          className="p-2 rounded-md text-gray-700 bg-white shadow-md focus:outline-none"
        >
          <Bars3Icon className="h-6 w-6" />
        </button>
      </div>

      {/* Sidebar for mobile */}
      <div
        className={clsx(
          'fixed inset-0 z-30 bg-gray-800 transform transition-transform duration-300 ease-in-out md:hidden',
          isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex justify-end p-4">
          <button
            onClick={toggleMobileMenu}
            className="p-2 rounded-md text-white focus:outline-none"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>
        <div className="flex flex-col h-full p-4 space-y-2">
          <div className="text-white text-xl font-bold mb-6 px-4">NewsMonitor</div>
          {navItems.map((item) => (
            <NavItem
              key={item.to}
              to={item.to}
              icon={item.icon}
              label={item.label}
              active={location.pathname.startsWith(item.to)}
            />
          ))}
        </div>
      </div>

      {/* Sidebar for desktop */}
      <div className="hidden md:flex md:flex-col md:w-64 md:bg-blue-900">
        <div className="flex flex-col h-0 flex-1">
          <div className="flex items-center h-16 px-4 bg-blue-800">
            <h1 className="text-white text-xl font-bold">NewsMonitor</h1>
          </div>
          <div className="flex-1 flex flex-col overflow-y-auto p-4 space-y-2">
            {navItems.map((item) => (
              <NavItem
                key={item.to}
                to={item.to}
                icon={item.icon}
                label={item.label}
                active={location.pathname.startsWith(item.to)}
              />
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;