import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'; // Added useQueryClient
import { ArrowLeftIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import api from '../../api/client'; // Ensure api is imported

const ReportGeneratePage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient(); // Added queryClient initialization
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: clients, isLoading: isLoadingClients } = useQuery({
    queryKey: ['clients'],
    queryFn: () => api.clientProfiles.getAll()
  });
  
  const generateReportMutation = useMutation({
    mutationFn: (data: { client_id: string; report_date?: string; send_email?: boolean; recipient_email?: string }) => {
      // First generate the report
      return api.reports.generate(data.client_id, data.report_date).then(result => {
        // If send_email is true, also send an email
        if (data.send_email && data.recipient_email && result.task_id) {
          // This assumes there's an endpoint to associate an email with a report task
          // If not, we might need to wait for the report to be ready before sending
          return api.reports.sendEmail(result.task_id, data.recipient_email).then(() => result);
        }
        return result;
      });
    },
    onSuccess: (data) => {
      toast.success('Report generation started');
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      // Wait for a moment before navigating to reports page since generation is async
      setTimeout(() => {
        navigate('/reports');
      }, 1500);
    },
    onError: (error: any) => {
      console.error('Failed to generate report:', error);
      toast.error(error.response?.data?.detail || 'Failed to generate report');
      setIsSubmitting(false);
    }
  });

  const formik = useFormik({
    initialValues: {
      client_id: '',
      report_date: new Date().toISOString().split('T')[0], // Today's date in YYYY-MM-DD format
      send_email: false,
      recipient_email: ''
    },
    validationSchema: Yup.object({
      client_id: Yup.string().required('Client is required'),
      report_date: Yup.date().required('Date is required'),
      recipient_email: Yup.string().email('Invalid email address').when('send_email', {
        is: true,
        then: (schema) => schema.required('Email is required when sending report'),
        otherwise: (schema) => schema.notRequired()
      })
    }),
    onSubmit: (values) => {
      setIsSubmitting(true);
      generateReportMutation.mutate(values);
    }
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center">
        <Link to="/reports" className="mr-4 text-gray-500 hover:text-gray-700">
          <ArrowLeftIcon className="h-5 w-5" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Generate Report</h1>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-4 sm:p-6">
          <form onSubmit={formik.handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="client_id" className="block text-sm font-medium text-gray-700">
                Client
              </label>
              <select
                id="client_id"
                name="client_id"
                className={`mt-1 block w-full rounded-md border ${
                  formik.touched.client_id && formik.errors.client_id 
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                } shadow-sm sm:text-sm`}
                value={formik.values.client_id}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                disabled={isLoadingClients || isSubmitting}
              >
                <option value="">Select a client</option>
                {clients?.map((client) => (
                  <option key={client.id} value={client.id}>{client.name}</option>
                ))}
              </select>
              {formik.touched.client_id && formik.errors.client_id && (
                <p className="mt-1 text-sm text-red-600">{formik.errors.client_id}</p>
              )}
            </div>

            <div>
              <label htmlFor="report_date" className="block text-sm font-medium text-gray-700">
                Report Date
              </label>
              <input
                id="report_date"
                name="report_date"
                type="date"
                className={`mt-1 block w-full rounded-md border ${
                  formik.touched.report_date && formik.errors.report_date 
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                } shadow-sm sm:text-sm`}
                value={formik.values.report_date}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                disabled={isSubmitting}
              />
              {formik.touched.report_date && formik.errors.report_date && (
                <p className="mt-1 text-sm text-red-600">{formik.errors.report_date}</p>
              )}
              <p className="mt-1 text-xs text-gray-500">
                This will generate a report covering news up to the selected date
              </p>
            </div>

            <div className="relative flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="send_email"
                  name="send_email"
                  type="checkbox"
                  className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                  checked={formik.values.send_email}
                  onChange={formik.handleChange}
                  disabled={isSubmitting}
                />
              </div>
              <div className="ml-3 text-sm">
                <label htmlFor="send_email" className="font-medium text-gray-700">
                  Send report via email when ready
                </label>
              </div>
            </div>

            {formik.values.send_email && (
              <div>
                <label htmlFor="recipient_email" className="block text-sm font-medium text-gray-700">
                  Recipient Email
                </label>
                <input
                  id="recipient_email"
                  name="recipient_email"
                  type="email"
                  className={`mt-1 block w-full rounded-md border ${
                    formik.touched.recipient_email && formik.errors.recipient_email 
                      ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                  } shadow-sm sm:text-sm`}
                  placeholder="client@example.com"
                  value={formik.values.recipient_email}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  disabled={isSubmitting}
                />
                {formik.touched.recipient_email && formik.errors.recipient_email && (
                  <p className="mt-1 text-sm text-red-600">{formik.errors.recipient_email}</p>
                )}
              </div>
            )}

            <div className="flex justify-end">
              <Link
                to="/reports"
                className="mr-3 px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </Link>
              <button
                type="submit"
                disabled={isSubmitting || !formik.isValid}
                className="px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <div className="flex items-center">
                  <DocumentTextIcon className="-ml-1 mr-2 h-5 w-5" />
                  {isSubmitting ? 'Generating...' : 'Generate Report'}
                </div>
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg font-medium text-gray-900">About Report Generation</h3>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
          <div className="text-sm text-gray-500 space-y-4">
            <p>
              Reports analyze relevant news articles for the selected client profile and generate a comprehensive summary of key information.
            </p>
            <p>
              The report will include:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>An executive summary highlighting key insights</li>
              <li>Relevant articles sorted by importance</li>
              <li>Summaries tailored to the client's interests</li>
              <li>PDF export for sharing and archiving</li>
            </ul>
            <p>
              Report generation typically takes 1-2 minutes depending on the amount of relevant news to analyze.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportGeneratePage;