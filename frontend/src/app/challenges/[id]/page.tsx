import ChallengeDetailClient from "./client";

export function generateStaticParams() {
  return [{ id: '101' }, { id: '102' }, { id: '1' }, { id: '2' }];
}

export default function ChallengeDetailPage({ params }: { params: Promise<{ id: string }> }) {
  return <ChallengeDetailClient params={params} />;
}
