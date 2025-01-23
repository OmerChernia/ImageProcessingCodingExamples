import React, { useState } from 'react';

export default function Sliders({ label, min, max, step, onChange }) {
  const [value, setValue] = useState((min + max) / 2);

  const handleChange = (e) => {
    const val = parseFloat(e.target.value);
    setValue(val);
    if (onChange) onChange(val);
  };

  return (
    <div className="flex flex-col p-2">
      <label className="mb-1 font-semibold">{label}: {value}</label>
      <input
        type="range"
        min={min}
        max={max}
        step={step || "1"}
        value={value}
        onChange={handleChange}
      />
    </div>
  );
} 