/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect } from 'react';
import yaml from 'yaml';
import personasRaw from '../config/personas.yaml?raw';
import { Pencil, Trash2, Plus, X, Play } from 'lucide-react';

type Persona = { 
  label: string; 
  rules: string[]; 
  drafts: {
    minimal: string;
    honest: string;
    practical: string;
  };
  output: string;
};

// Fallback mapping to upgrade old structure to new structure
const parsePersonas = () => {
  const parsed = yaml.parse(personasRaw);
  const upgraded: Record<string, Persona> = {};
  for (const key in parsed) {
    const p = parsed[key];
    upgraded[key] = {
      label: p.label || key,
      rules: p.rules || [],
      output: p.output || '',
      drafts: p.drafts || {
        minimal: "Acknowledged.",
        honest: p.draft || "Will do.",
        practical: "Got it, when do you need this by?"
      }
    };
  }
  return upgraded;
};

const INITIAL_PERSONAS: Record<string, Persona> = parsePersonas();

export default function App() {
  const [personas, setPersonas] = useState<Record<string, Persona>>(() => {
    const saved = localStorage.getItem('comms_hub_personas_v2');
    return saved ? JSON.parse(saved) : INITIAL_PERSONAS;
  });

  useEffect(() => {
    localStorage.setItem('comms_hub_personas_v2', JSON.stringify(personas));
  }, [personas]);

  const [activePersona, setActivePersona] = useState<string>('efficient');
  const personaData = personas[activePersona] || Object.values(personas)[0] || { label: 'Empty', rules: [], drafts: { minimal: '', honest: '', practical: '' }, output: '' };

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editId, setEditId] = useState<string>('');
  const [editForm, setEditForm] = useState<Persona>({ label: '', rules: [], drafts: { minimal: '', honest: '', practical: '' }, output: '' });

  // Simulator State
  const [rawInput, setRawInput] = useState("Hi Operator, it's Mum. Are you coming for dinner on Sunday? Bring your laundry from 42 Oak St. Love you.");
  const [redactedTrace, setRedactedTrace] = useState("Hi [OPERATOR], it's [MUM]. Are you coming for dinner on [DATE]? Bring your [ITEM] from [REDACTED_ADDRESS]. Love you.");
  const [activeDraftMode, setActiveDraftMode] = useState<'minimal'|'honest'|'practical'>('honest');
  const [isProcessing, setIsProcessing] = useState(false);

  // Terminal state
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    "[INFO] Fetching latest from chat.db...",
    "[WATCHER] 1 new message from 'Mum'",
    "[REDACTOR] Scrubbing PII: Address removed.",
    "[LINTER] Checking for 'SHAME CASCADE'... Not found."
  ]);

  const openCreate = () => {
    setEditId(`custom_${Date.now()}`);
    setEditForm({ label: 'New Persona', rules: ['- Rule 1'], drafts: { minimal: 'Yes.', honest: 'I think so.', practical: 'Yes, when?' }, output: 'persona_custom' });
    setIsModalOpen(true);
  };

  const openEdit = (id: string) => {
    setEditId(id);
    setEditForm(personas[id]);
    setIsModalOpen(true);
  };

  const savePersona = () => {
    setPersonas(prev => ({ ...prev, [editId]: editForm }));
    setActivePersona(editId);
    setIsModalOpen(false);
  };

  const deletePersona = (id: string) => {
    const newPersonas = { ...personas };
    delete newPersonas[id];
    setPersonas(newPersonas);
    if (activePersona === id) {
      setActivePersona(Object.keys(newPersonas)[0] || '');
    }
  };

  const runSimulation = () => {
    setIsProcessing(true);
    setTerminalLogs(["[INFO] Processing manual input..."]);
    
    // Simulate pipeline delay
    setTimeout(() => {
      let redacted = rawInput
        .replace(/Mum/gi, '[MUM]')
        .replace(/Operator/gi, '[OPERATOR]')
        .replace(/\d+\s+\w+\s+(St|Rd|Ave|Dr|Cres|Blvd|Ct|Pl|Way|Tce|Pde)/gi, '[REDACTED_ADDRESS]');
      
      setRedactedTrace(redacted);
      setTerminalLogs(prev => [
        ...prev, 
        "[WATCHER] Manual override triggered",
        "[REDACTOR] Scrubbing PII elements...",
        `[DRAFTER] Applying Gemini 2.0 Flash with context: ${personaData.output}`,
        "[LINTER] Rule checks passed successfully."
      ]);
      setIsProcessing(false);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="w-full max-w-[1024px] h-[768px] bg-[#0A0A0B] text-gray-300 font-sans p-6 overflow-hidden flex flex-col border-4 border-[#1A1A1C] rounded-xl shadow-2xl relative">
        {/* Modal Overlay */}
        {isModalOpen && (
          <div className="absolute inset-0 bg-black/80 flex items-center justify-center z-50">
            <div className="bg-[#141417] border border-gray-800 rounded-lg p-6 w-[500px] flex flex-col gap-4 shadow-2xl">
              <div className="flex justify-between items-center">
                <h2 className="text-white font-bold">Edit Persona</h2>
                <button onClick={() => setIsModalOpen(false)} className="text-gray-500 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs text-gray-500 uppercase">Label</label>
                <input 
                  type="text"
                  value={editForm.label}
                  onChange={e => setEditForm({ ...editForm, label: e.target.value })}
                  className="bg-black border border-gray-800 rounded p-2 text-sm text-white outline-none focus:border-sky-500"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs text-gray-500 uppercase">Rules (one per line)</label>
                <textarea 
                  value={editForm.rules.join('\n')}
                  onChange={e => setEditForm({ ...editForm, rules: e.target.value.split('\n') })}
                  className="bg-black border border-gray-800 rounded p-2 text-sm text-white outline-none focus:border-sky-500 min-h-[80px]"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs text-gray-500 uppercase">Draft: Minimal</label>
                <textarea 
                  value={editForm.drafts.minimal}
                  onChange={e => setEditForm({ ...editForm, drafts: { ...editForm.drafts, minimal: e.target.value } })}
                  className="bg-black border border-gray-800 rounded p-2 text-sm text-white outline-none focus:border-sky-500 h-16"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs text-gray-500 uppercase">Draft: Honest</label>
                <textarea 
                  value={editForm.drafts.honest}
                  onChange={e => setEditForm({ ...editForm, drafts: { ...editForm.drafts, honest: e.target.value } })}
                  className="bg-black border border-gray-800 rounded p-2 text-sm text-white outline-none focus:border-sky-500 h-16"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs text-gray-500 uppercase">Draft: Practical</label>
                <textarea 
                  value={editForm.drafts.practical}
                  onChange={e => setEditForm({ ...editForm, drafts: { ...editForm.drafts, practical: e.target.value } })}
                  className="bg-black border border-gray-800 rounded p-2 text-sm text-white outline-none focus:border-sky-500 h-16"
                />
              </div>
              <div className="flex flex-col gap-2 pt-2">
                <label className="text-xs text-gray-500 uppercase">Output Context</label>
                <input 
                  type="text"
                  value={editForm.output}
                  onChange={e => setEditForm({ ...editForm, output: e.target.value })}
                  className="bg-black border border-gray-800 rounded p-2 text-sm text-white outline-none focus:border-sky-500"
                />
              </div>
              <div className="flex justify-end gap-3 mt-4">
                <button onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-xs font-bold text-gray-400 hover:text-white transition-colors">
                  CANCEL
                </button>
                <button onClick={savePersona} className="px-4 py-2 text-xs font-bold bg-sky-500 text-black rounded hover:bg-sky-400 transition-colors">
                  SAVE PERSONA
                </button>
              </div>
            </div>
          </div>
        )}

        <header className="flex justify-between items-center mb-6 border-b border-gray-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sky-500 rounded flex items-center justify-center text-black font-black">
              CH
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white">
                COMMS HUB <span className="text-sky-500 font-mono text-xs ml-2 uppercase">v1.0.0-Stable</span>
              </h1>
              <p className="text-[10px] uppercase tracking-widest text-gray-500">
                MacOS CLI Agent • Gemini 3.1 Pro Integrated
              </p>
            </div>
          </div>
          <div className="flex gap-6">
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-gray-500 uppercase">Watcher</span>
              <span className="text-emerald-500 text-xs font-mono">● RUNNING</span>
            </div>
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-gray-500 uppercase">Drafter</span>
              <span className="text-emerald-500 text-xs font-mono">● CONNECTED</span>
            </div>
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-gray-500 uppercase">Uptime</span>
              <span className="text-white text-xs font-mono">14:22:04</span>
            </div>
          </div>
        </header>

        <main className="flex-1 grid grid-cols-1 md:grid-cols-12 gap-6 min-h-0">
          <aside className="md:col-span-4 lg:col-span-3 flex flex-col gap-4">
            <div className="bg-[#141417] rounded-lg p-4 border border-gray-800 flex-1 flex flex-col overflow-hidden">
              <h3 className="text-xs font-semibold text-gray-400 uppercase mb-3 flex items-center gap-2">
                <span className="w-2 h-2 bg-sky-500 rounded-full"></span> Inbound Stream
              </h3>
              <div className="space-y-3 overflow-y-auto pr-1">
                <div className="p-2 bg-[#1C1C21] rounded border-l-2 border-sky-500">
                  <div className="flex justify-between mb-1">
                    <span className="text-[10px] font-bold text-sky-400">Mum</span>
                    <span className="text-[9px] text-gray-500 uppercase">12:04 PM</span>
                  </div>
                  <p className="text-xs text-gray-300 line-clamp-2 italic">"Don't forget the laundry..."</p>
                </div>
                <div className="p-2 bg-transparent opacity-60 rounded border border-gray-800">
                  <div className="flex justify-between mb-1">
                    <span className="text-[10px] font-bold text-gray-400">Operator</span>
                    <span className="text-[9px] text-gray-500 uppercase">11:58 AM</span>
                  </div>
                  <p className="text-xs text-gray-500 line-clamp-1">"Project files are ready for..."</p>
                </div>
                <div className="p-2 bg-transparent opacity-40 rounded border border-gray-800">
                  <div className="flex justify-between mb-1">
                    <span className="text-[10px] font-bold text-gray-400">Partner</span>
                    <span className="text-[9px] text-gray-500 uppercase">11:30 AM</span>
                  </div>
                  <p className="text-xs text-gray-600 line-clamp-1">"Can you pick up milk?"</p>
                </div>
              </div>
            </div>
            <div className="bg-[#141417] rounded-lg p-4 border border-gray-800 flex flex-col min-h-[160px] flex-1">
              <h3 className="text-xs font-semibold text-gray-400 uppercase mb-3 flex justify-between items-center">
                Voice Personas
              </h3>
              <div className="grid grid-cols-2 gap-2 overflow-y-auto mb-3 pr-1">
                {Object.entries(personas).map(([key, p]) => (
                  <button
                    key={key}
                    onClick={() => setActivePersona(key)}
                    className={`flex flex-col text-left p-2.5 rounded border transition-colors ${
                      activePersona === key 
                        ? 'bg-sky-900/20 border-sky-500/50' 
                        : 'bg-black border-gray-800 hover:border-gray-600'
                    }`}
                  >
                    <span className={`text-[10px] font-bold truncate w-full ${activePersona === key ? 'text-sky-400' : 'text-gray-300'}`}>
                      {p.label}
                    </span>
                    <span className="text-[9px] text-gray-500 font-mono mt-1 w-full opacity-80 line-clamp-2">
                      {p.rules.length > 0 ? p.rules.map(r => r.replace(/^- /, '')).join(', ') : 'No rules'}
                    </span>
                  </button>
                ))}
              </div>
              <div className="mt-auto pt-3 border-t border-gray-800 flex gap-2 relative">
                <button onClick={() => openEdit(activePersona)} className="flex-1 bg-black border border-gray-800 hover:bg-gray-800 text-gray-400 text-[10px] uppercase py-1.5 rounded flex items-center justify-center gap-1 transition-colors" title="Edit Persona">
                  <Pencil className="w-3 h-3" /> Edit
                </button>
                <button onClick={() => deletePersona(activePersona)} className="w-8 bg-black border border-gray-800 hover:bg-red-900/40 text-red-500/70 hover:text-red-500 text-[10px] uppercase py-1.5 rounded flex items-center justify-center transition-colors" title="Delete Persona">
                  <Trash2 className="w-3 h-3" />
                </button>
                <button onClick={openCreate} className="flex-1 bg-sky-900/30 border border-sky-900 hover:bg-sky-900/50 text-sky-400 text-[10px] uppercase py-1.5 rounded flex items-center justify-center gap-1 transition-colors" title="New Persona">
                  <Plus className="w-3 h-3" /> Create
                </button>
              </div>
            </div>
          </aside>

          <section className="md:col-span-8 lg:col-span-9 flex flex-col gap-6">
            <div className="bg-[#141417] rounded-lg p-6 border border-gray-800 grid grid-cols-1 lg:grid-cols-2 gap-8 flex-shrink-0 relative">
              
              {/* Simulator Run Button */}
              <button 
                onClick={runSimulation}
                disabled={isProcessing}
                className="absolute -top-3 -right-3 bg-sky-500 hover:bg-sky-400 text-black px-4 py-1.5 rounded-full font-bold text-[10px] flex items-center gap-1.5 shadow-lg transition-colors disabled:opacity-50"
              >
                <Play className="w-3 h-3" />
                {isProcessing ? 'PROCESSING...' : 'RUN PIPELINE'}
              </button>

              <div className="space-y-4">
                <div className="flex flex-col h-1/2">
                  <h4 className="text-[10px] text-gray-500 uppercase font-bold mb-2 tracking-widest flex justify-between">
                    Raw Input
                    <span className="text-[9px] text-emerald-500">EDITABLE</span>
                  </h4>
                  <textarea 
                    value={rawInput}
                    onChange={e => setRawInput(e.target.value)}
                    className="bg-black/40 p-3 rounded font-mono text-xs border border-gray-800 leading-relaxed text-white  outline-none focus:border-sky-500 resize-none flex-1"
                  />
                </div>
                <div>
                  <h4 className="text-[10px] text-gray-500 uppercase font-bold mb-2 tracking-widest">
                    Redacted Trace
                  </h4>
                  <div className="bg-black/40 p-3 rounded font-mono text-xs border border-gray-800 leading-relaxed text-emerald-400/80 min-h-[60px]">
                    {isProcessing ? <span className="animate-pulse">...</span> : redactedTrace}
                  </div>
                </div>
              </div>
              <div className="space-y-4 flex flex-col">
                <div className="flex-1 flex flex-col">
                  <h4 className="text-[10px] text-sky-500 uppercase font-bold mb-2 tracking-widest flex gap-2">
                    Gemini 2.0
                    <div className="flex bg-black border border-gray-800 rounded p-0.5">
                      {(['minimal', 'honest', 'practical'] as const).map(mode => (
                        <button
                          key={mode}
                          onClick={() => setActiveDraftMode(mode)}
                          className={`px-2 py-0.5 rounded text-[9px] ${activeDraftMode === mode ? 'bg-sky-900/40 text-sky-400' : 'text-gray-500 hover:text-gray-300'}`}
                        >
                          {mode.toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </h4>
                  <div className="bg-[#1C1C21] p-4 rounded-lg border border-sky-900/30 shadow-inner relative flex-1 flex flex-col justify-center">
                    <div className="absolute top-2 right-2 text-[8px] bg-sky-900/40 text-sky-400 px-1.5 py-0.5 rounded">
                      JSON_MODE
                    </div>
                    {isProcessing ? (
                      <span className="text-sm text-gray-500 italic animate-pulse">Generating drafts...</span>
                    ) : (
                      <p className="text-sm text-white italic leading-relaxed">
                        "{personaData.drafts[activeDraftMode]}"
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-1 bg-black/40 p-2 rounded border border-gray-800">
                    <span className="text-[9px] text-gray-500 uppercase block mb-1">Linter Status</span>
                    <span className="text-emerald-500 text-[10px] font-bold tracking-widest uppercase">
                      CLEAN - NO FLAGS
                    </span>
                  </div>
                  <div className="flex-1 bg-black/40 p-2 rounded border border-gray-800">
                    <span className="text-[9px] text-gray-500 uppercase block mb-1">Token Cost</span>
                    <span className="text-white text-[10px] font-mono">0.00042 USD</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex-1 bg-black rounded border border-gray-800 font-mono text-xs p-4 overflow-y-auto relative shadow-2xl min-h-[200px]">
              <div className="absolute top-3 right-4 flex gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-gray-800"></div>
                <div className="w-2.5 h-2.5 rounded-full bg-gray-800"></div>
                <div className="w-2.5 h-2.5 rounded-full bg-gray-800"></div>
              </div>
              <div className="space-y-1.5 text-gray-400 pt-1">
                <p>
                  <span className="text-emerald-500">user@macbook</span>:<span className="text-sky-500">~/commshub</span>$ ./commshub status
                </p>
                {terminalLogs.map((log, i) => (
                  <p key={i} className={log.startsWith('[INFO]') ? 'text-gray-600 italic' : ''}>{log}</p>
                ))}
                
                {!isProcessing && (
                  <>
                    <p className="text-white font-bold py-1">
                      Draft: "{personaData.drafts[activeDraftMode]}"
                    </p>
                    <p>
                      <span className="text-sky-500 uppercase font-bold">{"[SEND? (Y/N/Edit)]:"}</span>{" "}
                      <span className="animate-pulse bg-sky-500 text-sky-500 w-2 inline-block">_</span>
                    </p>
                  </>
                )}
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
