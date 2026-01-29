import { useNavigate } from 'react-router-dom'
import { Home } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <h1 className="text-9xl font-extrabold tracking-widest text-muted-foreground">404</h1>
      <div className="mt-4 mb-8">
        <h2 className="text-2xl font-semibold">Page non trouvee</h2>
        <p className="mt-2 text-muted-foreground">
          La page que vous recherchez n'existe pas ou a ete deplacee.
        </p>
      </div>
      <Button onClick={() => navigate('/dashboard')}>
        <Home className="mr-2 h-4 w-4" />
        Retour au tableau de bord
      </Button>
    </div>
  )
}
