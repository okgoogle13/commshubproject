/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export default function App() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="w-full max-w-[1024px] h-[768px] bg-[#0A0A0B] text-gray-300 font-sans p-6 overflow-hidden flex flex-col border-4 border-[#1A1A1C] rounded-xl shadow-2xl">
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
            <div className="bg-[#141417] rounded-lg p-4 border border-gray-800 h-40">
              <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">Voice Persona</h3>
              <div className="text-xs font-mono leading-relaxed">
                <p className="text-sky-500">- Efficient / Dry</p>
                <p className="text-gray-500">- No emojis</p>
                <p className="text-gray-500">- Lowercase style</p>
                <p className="text-gray-500">- Affirmative closures</p>
              </div>
            </div>
          </aside>

          <section className="md:col-span-8 lg:col-span-9 flex flex-col gap-6">
            <div className="bg-[#141417] rounded-lg p-6 border border-gray-800 grid grid-cols-1 lg:grid-cols-2 gap-8 flex-shrink-0">
              <div className="space-y-4">
                <div>
                  <h4 className="text-[10px] text-gray-500 uppercase font-bold mb-2 tracking-widest">
                    Raw Input
                  </h4>
                  <div className="bg-black/40 p-3 rounded font-mono text-xs border border-gray-800 leading-relaxed text-gray-400">
                    "Hi Operator, it's Mum. Are you coming for dinner on Sunday? Bring your laundry from 42 Oak St. Love you."
                  </div>
                </div>
                <div>
                  <h4 className="text-[10px] text-gray-500 uppercase font-bold mb-2 tracking-widest">
                    Redacted Trace
                  </h4>
                  <div className="bg-black/40 p-3 rounded font-mono text-xs border border-gray-800 leading-relaxed text-emerald-400/80">
                    "Hi [OPERATOR], it's [MUM]. Are you coming for dinner on [DATE]? Bring your [ITEM] from [REDACTED_ADDRESS]. Love you."
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <h4 className="text-[10px] text-sky-500 uppercase font-bold mb-2 tracking-widest">
                    Gemini 3.1 Draft
                  </h4>
                  <div className="bg-[#1C1C21] p-4 rounded-lg border border-sky-900/30 shadow-inner relative">
                    <div className="absolute top-2 right-2 text-[8px] bg-sky-900/40 text-sky-400 px-1.5 py-0.5 rounded">
                      JSON_MODE
                    </div>
                    <p className="text-sm text-white italic leading-relaxed">
                      "i'll be there for dinner. will bring the laundry as requested. see you Sunday. thanks."
                    </p>
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
                <p className="text-gray-600 italic">[INFO] Fetching latest from chat.db...</p>
                <p>[WATCHER] 1 new message from 'Mum'</p>
                <p>[REDACTOR] Scrubbing PII: Address removed.</p>
                <p>[DRAFTER] Gemini context: persona_efficient_v2</p>
                <p>[LINTER] Checking for 'SHAME CASCADE'... Not found.</p>
                <p>[LINTER] Checking for 'UNVERIFIED PROMISE'... Not found.</p>
                <p className="text-white font-bold py-1">
                  Draft: "i'll be there for dinner. will bring the laundry as requested. see you Sunday. thanks."
                </p>
                <p>
                  <span className="text-sky-500 uppercase font-bold">{"[SEND? (Y/N/Edit)]:"}</span>{" "}
                  <span className="animate-pulse bg-sky-500 text-sky-500 w-2 inline-block">_</span>
                </p>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
