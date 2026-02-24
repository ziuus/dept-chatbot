import "./globals.css";

export const metadata = {
  title: "Department Voice Assistant",
  description: "Ask department questions with voice and hear spoken answers"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
