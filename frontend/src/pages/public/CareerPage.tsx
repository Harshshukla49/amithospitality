import React, { useState } from 'react';
import {
  Sparkles,
  Briefcase,
  Users,
  Award,
  Upload,
  CheckCircle,
  AlertCircle,
  Shield,
  ArrowRight,
  HeartHandshake,
} from 'lucide-react';

export const CareerPage: React.FC = () => {
  const [fullName, setFullName] = useState('');
  const [contactNumber, setContactNumber] = useState('');
  const [email, setEmail] = useState('');
  const [department, setDepartment] = useState('Restaurant Operations');
  const [yearsExperience, setYearsExperience] = useState('1-3 Years');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [coverNote, setCoverNote] = useState('');

  const [submitting, setSubmitting] = useState(false);
  const [submittedRef, setSubmittedRef] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const departments = [
    'Restaurant Operations',
    'Kitchen & Culinary',
    'Food & Beverage / Mixology',
    'Guest Relations & Front Desk',
    'Restaurant & F&B Management',
    'Marketing & Brand Communications',
    'Corporate Sales & Banquets',
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!validTypes.includes(file.type)) {
        setErrorMessage('Please upload a PDF or Word document (.pdf, .doc, .docx).');
        setResumeFile(null);
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setErrorMessage('Resume file size must not exceed 5MB.');
        setResumeFile(null);
        return;
      }
      setErrorMessage(null);
      setResumeFile(file);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!fullName.trim() || !contactNumber.trim() || !email.trim()) {
      setErrorMessage('Please fill in all required contact information.');
      return;
    }

    setSubmitting(true);
    // Simulate safe application upload and reference generation
    setTimeout(() => {
      setSubmitting(false);
      setSubmittedRef(`APP-${Date.now().toString().slice(-6)}`);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-obsidian-950 text-slate-100 font-sans pb-24">
      {/* 1. HERO HEADER */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 border-b border-slate-800 bg-gradient-to-b from-charcoal-900 via-obsidian-950 to-obsidian-950">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-charcoal-900 border border-gold-400/40 text-gold-300 text-xs font-mono uppercase tracking-widest">
            <Briefcase className="w-3.5 h-3.5 text-gold-400" />
            <span>Hospitality Careers • Amit Hospitality LLP</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-serif font-bold text-white tracking-tight">
            Build Your Career in Premier Hospitality
          </h1>
          <p className="text-sm sm:text-base text-slate-300 font-light max-w-2xl mx-auto leading-relaxed">
            Join Kolkata's dynamic culinary, mixology, and guest experience brigades across Lord of the Drinks, Veneto Kitchen &amp; Bar, and The Warehouse Cafe.
          </p>
        </div>
      </section>

      {/* 2. CULTURE & OPPORTUNITIES */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-charcoal-900 border border-slate-800 space-y-3">
            <Users className="w-6 h-6 text-gold-400" />
            <h3 className="font-serif font-bold text-lg text-white">Inspiring Team Culture</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              We champion mutual respect, creativity, and meritocracy. Every team member from commis chef to floor host is valued.
            </p>
          </div>
          <div className="p-6 rounded-2xl bg-charcoal-900 border border-slate-800 space-y-3">
            <Award className="w-6 h-6 text-gold-400" />
            <h3 className="font-serif font-bold text-lg text-white">World-Class Mentorship</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Work alongside accomplished executive chefs, master mixologists, and experienced F&amp;B directors in high-volume properties.
            </p>
          </div>
          <div className="p-6 rounded-2xl bg-charcoal-900 border border-slate-800 space-y-3">
            <HeartHandshake className="w-6 h-6 text-gold-400" />
            <h3 className="font-serif font-bold text-lg text-white">Career Progression</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              We prioritize internal promotions and career pathways as our hospitality footprint expands across Eastern India.
            </p>
          </div>
        </div>
      </section>

      {/* 3. APPLICATION WORKFLOW */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-3xl mx-auto">
        <div className="p-8 sm:p-10 rounded-3xl bg-charcoal-900 border border-gold-400/30 shadow-2xl space-y-6">
          <div>
            <span className="text-xs font-mono uppercase tracking-widest text-gold-400 font-semibold">
              General Career Application
            </span>
            <h2 className="text-2xl font-serif font-bold text-white mt-1">
              Submit Your Profile
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              While we do not list speculative openings, our HR talent team reviews every general application for active and upcoming departmental vacancies.
            </p>
          </div>

          {errorMessage && (
            <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-500/50 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {submittedRef ? (
            <div className="text-center py-8 space-y-4 animate-scale-up">
              <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-400/50 flex items-center justify-center mx-auto text-emerald-400">
                <CheckCircle className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-serif font-bold text-white">
                Application Received!
              </h3>
              <p className="text-xs text-slate-300 max-w-md mx-auto leading-relaxed">
                Thank you for applying to Amit Hospitality LLP. Your profile reference is <strong className="text-gold-300 font-mono">{submittedRef}</strong>. Our human resources team will contact you if your skills match an active opening.
              </p>
              <button
                onClick={() => setSubmittedRef(null)}
                className="px-6 py-2 rounded-xl bg-charcoal-800 text-slate-200 text-xs font-semibold hover:bg-charcoal-700 transition"
              >
                Submit Another Application
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Candidate Name"
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Contact Phone Number *
                  </label>
                  <input
                    type="tel"
                    value={contactNumber}
                    onChange={(e) => setContactNumber(e.target.value)}
                    placeholder="+91 9831XXXXXX"
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="candidate@example.com"
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Target Department *
                  </label>
                  <select
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  >
                    {departments.map((d) => (
                      <option key={d} value={d}>
                        {d}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Years of Hospitality Experience
                  </label>
                  <select
                    value={yearsExperience}
                    onChange={(e) => setYearsExperience(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  >
                    <option value="Entry / Fresher">Entry / Fresher</option>
                    <option value="1-3 Years">1-3 Years</option>
                    <option value="3-5 Years">3-5 Years</option>
                    <option value="5-10 Years">5-10 Years</option>
                    <option value="10+ Years">10+ Years (Senior Management)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Attach Resume (PDF / DOCX, max 5MB)
                  </label>
                  <label className="flex items-center gap-2 w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-dashed border-slate-700 hover:border-gold-400 cursor-pointer text-xs text-slate-400 truncate">
                    <Upload className="w-4 h-4 text-gold-400 shrink-0" />
                    <span className="truncate">{resumeFile ? resumeFile.name : 'Choose file...'}</span>
                    <input
                      type="file"
                      onChange={handleFileChange}
                      accept=".pdf,.doc,.docx"
                      className="hidden"
                    />
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Brief Introduction &amp; Core Strengths
                </label>
                <textarea
                  rows={3}
                  value={coverNote}
                  onChange={(e) => setCoverNote(e.target.value)}
                  placeholder="Share a short summary of your hospitality background and career aspirations..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs hover:brightness-110 transition shadow-gold-glow disabled:opacity-50"
              >
                {submitting ? 'Submitting Application...' : 'Submit Career Application'}
              </button>
            </form>
          )}
        </div>
      </section>
    </div>
  );
};
