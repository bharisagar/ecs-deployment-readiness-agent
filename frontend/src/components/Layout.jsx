import { Activity, ClipboardCheck, History, LayoutDashboard, Network } from "lucide-react";
import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/new", label: "New Check", icon: ClipboardCheck },
  { to: "/history", label: "History", icon: History },
  { to: "/about", label: "Architecture", icon: Network }
];

export default function Layout({ children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Activity size={24} aria-hidden="true" />
          <div>
            <strong>ECS Guard</strong>
            <span>Readiness Agent</span>
          </div>
        </div>
        <nav>
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} end={to === "/"}>
              <Icon size={18} aria-hidden="true" />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
