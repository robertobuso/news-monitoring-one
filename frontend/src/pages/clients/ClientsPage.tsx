import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  PlusIcon, 
  MagnifyingGlassIcon, 
  ChevronRightIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import api from '../../api/client';

const ClientsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  
  const { data: clients, isLoading, error } = useQuery({
    queryKey: ['clients'],
    queryFn: () => api.clientProfiles.getAll()
  });

  // Filter clients based on search term
  const filteredClients = clients?.filter((client: any) => 
    client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    client.industry.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Client Profiles</h1>
        <Link
          to="/clients/create"
          className="mt-3 sm:mt-0 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
          New Client Profile
        </Link>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-4 sm:p-6 border-b">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Search clients..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        {isLoading ? (
          <div className="p-4 sm:p-6">
            <div className="animate-pulse space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        ) : error ? (
          <div className="p-4 sm:p-6 text-center text-red-500">
            Error loading clients. Please try again.
          </div>
        ) : filteredClients?.length === 0 ? (
          <div className="p-4 sm:p-6 text-center text-gray-500">
            {searchTerm ? 'No clients match your search.' : 'No clients found. Create your first client profile.'}
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {filteredClients?.map((client: any) => (
              <li key={client.id}>
                <Link
                  to={`/clients/${client.id}`}
                  className="block hover:bg-gray-50"
                >
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-blue-600 font-medium text-lg">
                            {client.name.charAt(0)}
                          </span>
                        </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-900">{client.name}</p>
                          <p className="text-sm text-gray-500">{client.industry}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          client.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {client.is_active ? 'Active' : 'Inactive'}
                        </span>
                        <ChevronRightIcon className="ml-4 h-5 w-5 text-gray-400" />
                      </div>
                    </div>
                    <div className="mt-2 sm:flex sm:justify-between">
                      <div className="sm:flex">
                        <p className="flex items-center text-sm text-gray-500">
                          <DocumentTextIcon className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
                          {client.keywords.length} keywords
                        </p>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                        <p>Created on {new Date(client.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ClientsPage;