import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-green-700 text-white px-6 py-3 flex items-center justify-between shadow-md">
      <div className="flex items-center gap-6">
        <span className="text-xl font-bold tracking-tight">OptiShop</span>
        <Link to="/shop" className="text-sm hover:text-green-200 transition-colors">
          Shop
        </Link>
        {role === 'store_owner' && (
          <Link to="/dashboard" className="text-sm hover:text-green-200 transition-colors">
            Dashboard
          </Link>
        )}
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-green-200">{user?.sub}</span>
        <span className="text-xs bg-green-800 px-2 py-0.5 rounded-full capitalize">{role}</span>
        <button
          onClick={handleLogout}
          className="text-sm bg-white text-green-700 px-3 py-1 rounded hover:bg-green-100 transition-colors font-medium"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
