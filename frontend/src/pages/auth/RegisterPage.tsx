import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../../app/providers/AuthProvider';

const RegisterPage: React.FC = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const formik = useFormik({
    initialValues: {
      first_name: '',
      last_name: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
    validationSchema: Yup.object({
      first_name: Yup.string()
        .required('First name is required'),
      last_name: Yup.string()
        .required('Last name is required'),
      email: Yup.string()
        .email('Invalid email address')
        .required('Email is required'),
      password: Yup.string()
        .min(8, 'Password must be at least 8 characters')
        .matches(/[0-9]/, 'Password must contain at least one number')
        .matches(/[A-Z]/, 'Password must contain at least one uppercase letter')
        .required('Password is required'),
      confirmPassword: Yup.string()
        .oneOf([Yup.ref('password')], 'Passwords must match')
        .required('Confirm password is required'),
    }),
    onSubmit: async (values, { setSubmitting, setStatus }) => {
      try {
        await register({
          first_name: values.first_name,
          last_name: values.last_name,
          email: values.email,
          password: values.password,
        });
        navigate('/dashboard');
      } catch (error: any) {
        setStatus(error.response?.data?.detail || 'Registration failed');
      } finally {
        setSubmitting(false);
      }
    },
  });

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link to="/auth/login" className="font-medium text-blue-600 hover:text-blue-500">
              sign in to your existing account
            </Link>
          </p>
        </div>
        
        {formik.status && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <span className="block sm:inline">{formik.status}</span>
          </div>
        )}
        
        <form className="mt-8 space-y-6" onSubmit={formik.handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 mb-4">
              <div>
                <label htmlFor="first_name" className="sr-only">First name</label>
                <input
                  id="first_name"
                  name="first_name"
                  type="text"
                  autoComplete="given-name"
                  required
                  className={`appearance-none rounded-md relative block w-full px-3 py-2 border ${
                    formik.touched.first_name && formik.errors.first_name 
                      ? 'border-red-300 text-red-900 placeholder-red-300'
                      : 'border-gray-300 placeholder-gray-500 text-gray-900'
                  } focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm`}
                  placeholder="First name"
                  value={formik.values.first_name}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                />
                {formik.touched.first_name && formik.errors.first_name && (
                  <div className="text-red-500 text-xs mt-1">{formik.errors.first_name}</div>
                )}
              </div>
              <div>
                <label htmlFor="last_name" className="sr-only">Last name</label>
                <input
                  id="last_name"
                  name="last_name"
                  type="text"
                  autoComplete="family-name"
                  required
                  className={`appearance-none rounded-md relative block w-full px-3 py-2 border ${
                    formik.touched.last_name && formik.errors.last_name 
                      ? 'border-red-300 text-red-900 placeholder-red-300'
                      : 'border-gray-300 placeholder-gray-500 text-gray-900'
                  } focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm`}
                  placeholder="Last name"
                  value={formik.values.last_name}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                />
                {formik.touched.last_name && formik.errors.last_name && (
                  <div className="text-red-500 text-xs mt-1">{formik.errors.last_name}</div>
                )}
              </div>
            </div>
            
            <div className="mb-4">
              <label htmlFor="email" className="sr-only">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className={`appearance-none rounded-md relative block w-full px-3 py-2 border ${
                  formik.touched.email && formik.errors.email 
                    ? 'border-red-300 text-red-900 placeholder-red-300'
                    : 'border-gray-300 placeholder-gray-500 text-gray-900'
                } focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm`}
                placeholder="Email address"
                value={formik.values.email}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              />
              {formik.touched.email && formik.errors.email && (
                <div className="text-red-500 text-xs mt-1">{formik.errors.email}</div>
              )}
            </div>
            
            <div className="mb-4">
              <label htmlFor="password" className="sr-only">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                className={`appearance-none rounded-md relative block w-full px-3 py-2 border ${
                  formik.touched.password && formik.errors.password 
                    ? 'border-red-300 text-red-900 placeholder-red-300'
                    : 'border-gray-300 placeholder-gray-500 text-gray-900'
                } focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm`}
                placeholder="Password"
                value={formik.values.password}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              />
              {formik.touched.password && formik.errors.password && (
                <div className="text-red-500 text-xs mt-1">{formik.errors.password}</div>
              )}
            </div>
            
            <div>
              <label htmlFor="confirmPassword" className="sr-only">Confirm password</label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                className={`appearance-none rounded-md relative block w-full px-3 py-2 border ${
                  formik.touched.confirmPassword && formik.errors.confirmPassword 
                    ? 'border-red-300 text-red-900 placeholder-red-300'
                    : 'border-gray-300 placeholder-gray-500 text-gray-900'
                } focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm`}
                placeholder="Confirm password"
                value={formik.values.confirmPassword}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              />
              {formik.touched.confirmPassword && formik.errors.confirmPassword && (
                <div className="text-red-500 text-xs mt-1">{formik.errors.confirmPassword}</div>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={formik.isSubmitting}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {formik.isSubmitting ? 'Creating account...' : 'Create account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterPage;