import PageHeader from '../components/PageHeader';

export default function ApiDocs() {
  const docsUrl = `${window.location.origin}/docs`;

  return (
    <>
      <PageHeader title="API Documentation" subtitle="Interactive Swagger REST OpenAPI specification details" />
      <div className="p-6 flex-1 flex flex-col overflow-hidden max-h-[calc(100vh-140px)]">
        <div className="flex-1 card-base overflow-hidden p-0 relative flex flex-col">
          <iframe
            src={docsUrl}
            title="FastAPI Swagger Documentation"
            className="w-full flex-1 border-0 bg-white"
          />
        </div>
      </div>
    </>
  );
}
