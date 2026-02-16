import FinisherHeader from "../components/BackgroundApp/FinisherHeader";

export default function RootLayout({ children }) {
  return (
    <>
    <FinisherHeader />
      <div className="app">{children}</div>
    </>
  );
}
