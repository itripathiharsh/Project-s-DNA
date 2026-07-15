import PageHeader from '../components/PageHeader';
import NotAvailable from '../components/NotAvailable';

export default function withMeta(title, subtitle, icon) {
  function Page() {
    return (
      <>
        <PageHeader title={title} subtitle={subtitle} />
        <NotAvailable title={title} icon={icon} />
      </>
    );
  }
  Page.displayName = title.replace(/\s/g, '');
  return Page;
}
