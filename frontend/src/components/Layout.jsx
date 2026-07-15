import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import MobileTopNav from './MobileTopNav';

export default function Layout() {
  return (
    <div className="h-screen flex overflow-hidden bg-background text-on-surface font-body-md text-body-md">
      <MobileTopNav />
      <Sidebar />
      <main className="flex-1 flex flex-col h-full pt-[36px] md:pt-0 md:ml-sidebar-width bg-surface overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
