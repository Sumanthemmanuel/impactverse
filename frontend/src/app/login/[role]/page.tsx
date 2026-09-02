import RoleLoginClient from "./client";

export function generateStaticParams() {
  return [
    { role: 'citizen' },
    { role: 'student' },
    { role: 'university' },
    { role: 'government' },
    { role: 'industry' }
  ];
}

export default function RoleLoginPage({ params }: { params: Promise<{ role: string }> }) {
  return <RoleLoginClient params={params} />;
}
