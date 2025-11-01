import React, { useState } from "react";

export const HamburgerMenu: React.FC = () => {
  const [open, setOpen] = useState(false);

  const menuItems = ["File", "Edit", "Layer", "Settings", "Help", "Exit"];

  return (
    <div style={{ position: "absolute", top: 10, left: 10, zIndex: 2000 }}>
      <button onClick={() => setOpen(!open)}>☰</button>
      {open && (
        <div style={{ background: "#222", color: "#fff", padding: 6, borderRadius: 4 }}>
          {menuItems.map(item => (
            <div key={item} style={{ padding: 4, cursor: "pointer" }} onClick={() => alert(item)}>
              {item}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
