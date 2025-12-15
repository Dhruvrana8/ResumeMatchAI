import Link from "next/link";

export function Header() {
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between border-b selection:bg-primary/30 px-6 py-4 lg:px-20">
      <div className="flex items-center gap-3">
        <div className="flex items-center justify-center size-10 rounded-lg bg-primary/10 text-primary">
          <span className="material-symbols-outlined text-2xl">
            description
          </span>
        </div>
        <h2 className="text-xl font-bold tracking-tight text-slate-900 text-white dark:text-white">
          Resume ATS Scanner
        </h2>
      </div>
      {/* TODO: Add navigation */}
      {/* <div className="hidden md:flex items-center gap-8">
        <nav className="flex gap-6">
          <Link
            href="#"
            className="text-sm font-medium hover:text-primary transition-colors text-slate-600 dark:text-slate-300"
          >
            Dashboard
          </Link>
          <Link
            href="#"
            className="text-sm font-medium hover:text-primary transition-colors text-slate-600 dark:text-slate-300"
          >
            Pricing
          </Link>
          <Link
            href="#"
            className="text-sm font-medium hover:text-primary transition-colors text-slate-600 dark:text-slate-300"
          >
            History
          </Link>
        </nav>
        <div className="h-6 w-px bg-gray-200 dark:bg-border-dark"></div>
        <button className="flex items-center gap-2 rounded-lg bg-primary px-5 py-2 text-sm font-bold text-white transition-all hover:bg-blue-600 active:scale-95 shadow-lg shadow-primary/25 cursor-pointer">
          Sign In
        </button>
      </div> */}
      <button className="md:hidden text-slate-600 dark:text-slate-300">
        <span className="material-symbols-outlined">menu</span>
      </button>
    </header>
  );
}
