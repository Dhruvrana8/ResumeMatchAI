export function Footer() {
  return (
    <footer className="mt-auto border-t border-gray-200 dark:border-border-dark py-8 text-center text-sm text-slate-500 dark:text-slate-500">
      <p>© 2025 Resume ATS Scanner. All rights reserved.</p>
      <p className="mt-2">
        Feel free to connect:
        <a
          href="https://www.linkedin.com/in/dhruv-rana-bb94661b4/"
          target="_blank"
          rel="noopener noreferrer"
          className="ml-2 text-blue-600 hover:underline dark:text-blue-400"
        >
          LinkedIn
        </a>
        <a
          href="https://github.com/Dhruvrana8"
          target="_blank"
          rel="noopener noreferrer"
          className="ml-2 text-blue-600 hover:underline dark:text-blue-400"
        >
          GitHub
        </a>
        <a
          href="mailto:dhruvrana4@gmail.com"
          className="ml-2 text-blue-600 hover:underline dark:text-blue-400"
        >
          Email
        </a>
      </p>
    </footer>
  );
}
