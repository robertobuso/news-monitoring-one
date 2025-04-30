import React, { useState, useEffect } from 'react';

interface ClientProfileFormProps {
  initialData?: {
    name: string;
    industry: string;
    description?: string;
    keywords: string[];
  };
  onSubmit: (formData: any) => void;
  isSubmitting?: boolean;
}

const ClientProfileForm: React.FC<ClientProfileFormProps> = ({ initialData, onSubmit, isSubmitting }) => {
  const [name, setName] = useState('');
  const [industry, setIndustry] = useState('');
  const [description, setDescription] = useState('');
  const [keywords, setKeywords] = useState<string[]>([]);
  const [keywordInput, setKeywordInput] = useState('');

  useEffect(() => {
    if (initialData) {
      setName(initialData.name);
      setIndustry(initialData.industry);
      setDescription(initialData.description || '');
      setKeywords(initialData.keywords || []);
    }
  }, [initialData]);

  const handleKeywordAdd = () => {
    if (keywordInput.trim() !== '' && !keywords.includes(keywordInput.trim())) {
      setKeywords([...keywords, keywordInput.trim()]);
      setKeywordInput('');
    }
  };

  const handleKeywordRemove = (keyword: string) => {
    setKeywords(keywords.filter(k => k !== keyword));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ name, industry, description, keywords });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700">Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Industry</label>
        <input
          type="text"
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          rows={3}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Keywords</label>
        <div className="flex space-x-2 mt-1">
          <input
            type="text"
            value={keywordInput}
            onChange={(e) => setKeywordInput(e.target.value)}
            className="flex-1 border border-gray-300 rounded-md shadow-sm p-2"
          />
          <button
            type="button"
            onClick={handleKeywordAdd}
            className="px-3 py-2 bg-blue-600 text-white rounded-md"
          >
            Add
          </button>
        </div>
        <div className="flex flex-wrap mt-2 gap-2">
          {keywords.map((k, i) => (
            <span
              key={i}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
            >
              {k}
              <button
                type="button"
                onClick={() => handleKeywordRemove(k)}
                className="ml-2 text-blue-500 hover:text-blue-700"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      <div>
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full inline-flex justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </form>
  );
};

export default ClientProfileForm;
