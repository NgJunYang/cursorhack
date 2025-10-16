import UploadPanel from './components/UploadPanel'
import RecentReports from './components/RecentReports'

export default function Page() {
  return (
    <main className="space-y-8">
      <UploadPanel />
      <RecentReports />
    </main>
  )
}
