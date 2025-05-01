import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import api from '../../api/client';  // Import the actual API client

const FeedCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    // Use the actual API call instead of the mock function
    mutationFn: (data: any) => api.feeds.create(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] });
      toast.success('Feed created successfully');
      navigate(`/feeds/${data.id}`);
    },
    onError: (error: any) => {
      console.error('Error creating feed:', error);
      toast.error(error.response?.data?.detail || 'Failed to create feed');
    }
  });

  const feedTypes = [
    { value: 'rss', label: 'RSS Feed' },
    { value: 'api', label: 'API' },
    { value: 'web', label: 'Web Scraper' }
  ];

  const formik = useFormik({
    initialValues: {
      name: '',
      url: '',
      type: 'rss',
      check_frequency: 60, // Default: 1 hour in minutes
      is_active: true
    },
    validationSchema: Yup.object({
      name: Yup.string().required('Name is required'),
      url: Yup.string()
        .url('Must be a valid URL')
        .required('URL is required'),
      type: Yup.string().required('Type is required'),
      check_frequency: Yup.number()
        .min(5, 'Minimum check frequency is 5 minutes')
        .required('Check frequency is required'),
    }),
    onSubmit: (values) => {
      createMutation.mutate(values);
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center">
        <Link to="/feeds" className="mr-4 text-gray-500 hover:text-gray-700">
          <ArrowLeftIcon className="h-5 w-5" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Add News Feed</h1>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-4 sm:p-6">
          <form onSubmit={formik.handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Feed Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                className={`mt-1 block w-full rounded-md border ${
                  formik.touched.name && formik.errors.name 
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                } shadow-sm sm:text-sm`}
                placeholder="Tech News"
                value={formik.values.name}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              />
              {formik.touched.name && formik.errors.name && (
                <p className="mt-1 text-sm text-red-600">{formik.errors.name}</p>
              )}
            </div>

            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700">
                Feed URL
              </label>
              <input
                id="url"
                name="url"
                type="text"
                className={`mt-1 block w-full rounded-md border ${
                  formik.touched.url && formik.errors.url 
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                } shadow-sm sm:text-sm`}
                placeholder="https://example.com/rss"
                value={formik.values.url}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              />
              {formik.touched.url && formik.errors.url && (
                <p className="mt-1 text-sm text-red-600">{formik.errors.url}</p>
              )}
            </div>

            <div>
              <label htmlFor="type" className="block text-sm font-medium text-gray-700">
                Feed Type
              </label>
              <select
                id="type"
                name="type"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                value={formik.values.type}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              >
                {feedTypes.map((type) => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
              {formik.touched.type && formik.errors.type && (
                <p className="mt-1 text-sm text-red-600">{formik.errors.type}</p>
              )}
            </div>

            <div>
              <label htmlFor="check_frequency" className="block text-sm font-medium text-gray-700">
                Check Frequency (minutes)
              </label>
              <input
                id="check_frequency"
                name="check_frequency"
                type="number"
                min="5"
                className={`mt-1 block w-full rounded-md border ${
                  formik.touched.check_frequency && formik.errors.check_frequency 
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                } shadow-sm sm:text-sm`}
                value={formik.values.check_frequency}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              />
              {formik.touched.check_frequency && formik.errors.check_frequency && (
                <p className="mt-1 text-sm text-red-600">{formik.errors.check_frequency}</p>
              )}
            </div>

            <div className="flex items-center">
              <input
                id="is_active"
                name="is_active"
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                checked={formik.values.is_active}
                onChange={formik.handleChange}
              />
              <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                Active
              </label>
            </div>

            <div className="flex justify-end">
              <Link
                to="/feeds"
                className="mr-3 px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </Link>
              <button
                type="submit"
                disabled={createMutation.isPending || !formik.isValid}
                className="px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {createMutation.isPending ? 'Saving...' : 'Save Feed'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default FeedCreatePage;