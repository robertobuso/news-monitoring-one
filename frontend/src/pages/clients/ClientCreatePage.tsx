import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import api from '../../api/client';
import ClientProfileForm from '../../components/client-profiles/ClientProfileForm';

const ClientCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (data: any) => api.clientProfiles.create(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      toast.success('Client profile created successfully');
      navigate(`/clients/${data.id}`);
    },
    onError: () => {
      toast.error('Failed to create client profile');
    }
  });

  const handleSubmit = (formData: any) => {
    createMutation.mutate(formData);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center">
        <Link to="/clients" className="mr-4 text-gray-500 hover:text-gray-700">
          <ArrowLeftIcon className="h-5 w-5" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Create Client Profile</h1>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-4 sm:p-6">
          <ClientProfileForm
            onSubmit={handleSubmit}
            isSubmitting={createMutation.isPending}
          />
        </div>
      </div>
    </div>
  );
};

export default ClientCreatePage;