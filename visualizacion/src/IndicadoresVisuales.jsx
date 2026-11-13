import { useTienda } from './estado.js'

export default function IndicadoresVisuales({ enLinea = false }) {
  const clima = useTienda((s) => s.clima)
  const velocidad = useTienda((s) => s.velocidad)
  const nivel = { sin: 0, ligera: 1, intensa: 2 }[clima]
  const nombre = { sin: 'Sin lluvia', ligera: 'Ligera', intensa: 'Intensa' }[clima]
  const angulo = { 1: -60, 4: -20, 10: 20, 30: 60 }[velocidad]
  return (
    <aside className={`indicadores-visuales ${enLinea ? 'en-linea' : ''}`} aria-label="Ambiente y velocidad de reproducción">
      <div className="mini-indicador" role="img" aria-label={`Lluvia: ${nombre}`} title={`Lluvia: ${nombre}`}>
        <svg width="36" height="38" viewBox="0 0 36 38" aria-hidden="true">
          <defs><clipPath id="gota-clima"><path d="M18 3C15 9 7 16 7 23a11 11 0 0 0 22 0C29 16 21 9 18 3Z" /></clipPath></defs>
          <path d="M18 3C15 9 7 16 7 23a11 11 0 0 0 22 0C29 16 21 9 18 3Z" fill="#fff" stroke="#cbd5e1" strokeWidth="1.5" />
          <rect x="6" y={nivel === 2 ? 3 : nivel === 1 ? 20 : 36} width="24" height="34" fill="#2155eb" clipPath="url(#gota-clima)" />
          <path d="M12 24c0 4 2 6 5 6" stroke={nivel ? '#fff' : '#94a3b8'} strokeWidth="2" fill="none" strokeLinecap="round" />
        </svg>
        <div className="niveles-lluvia" aria-hidden="true">{[1, 2].map(n => <i key={n} className={nivel >= n ? 'encendido' : ''} />)}</div>
        <span>{nombre}</span>
      </div>
      <div className="mini-indicador" role="img" aria-label={`Velocidad de reproducción: ${velocidad} veces`} title="Velocidad de reproducción">
        <svg width="42" height="32" viewBox="0 0 42 32" aria-hidden="true">
          <path d="M5 25a16 16 0 1 1 32 0" fill="none" stroke="#e2e8f0" strokeWidth="4" strokeLinecap="round" />
          <path d="M5 25a16 16 0 0 1 16-16" fill="none" stroke="#2155eb" strokeWidth="4" strokeLinecap="round" />
          <g transform={`rotate(${angulo} 21 25)`}><path d="M21 25V12" stroke="#172033" strokeWidth="2" strokeLinecap="round" /></g>
          <circle cx="21" cy="25" r="3" fill="#2155eb" />
        </svg>
        <strong>×{velocidad}</strong>
        <span>Reproducción</span>
      </div>
    </aside>
  )
}
