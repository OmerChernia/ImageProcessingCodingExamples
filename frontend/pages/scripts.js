import React, { useState } from 'react';

export default function ScriptsPage() {
  const [output, setOutput] = useState("");

  // Generic function to call an endpoint
  async function runScript(endpoint) {
    setOutput("Running script... Please wait.");
    try {
      const res = await fetch(`http://localhost:8000/api/${endpoint}`);
      const data = await res.json();
      // data structure: {status: "ok"|"error", output: string, error?: string}
      if (data.status === "ok") {
        setOutput(data.output);
      } else {
        setOutput(`Error: ${data.error}\nOutput: ${data.output}`);
      }
    } catch (err) {
      setOutput(`Error calling script: ${err.message}`);
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Run Backend Scripts</h1>

      <button
        onClick={() => runScript("run_2pointer")}
        className="mr-4 px-4 py-2 bg-blue-600 text-white rounded"
      >
        Run 2PointerAlgo
      </button>

      <button
        onClick={() => runScript("run_transformations")}
        className="mr-4 px-4 py-2 bg-green-600 text-white rounded"
      >
        Run Transformations
      </button>

      <p className="mt-4 whitespace-pre-wrap">{output}</p>
    </div>
  );
} 