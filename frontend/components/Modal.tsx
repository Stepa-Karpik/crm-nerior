'use client'
export function Modal({ title, children, onClose }: { title: string; children: React.ReactNode; onClose: () => void }) {
  return <div className="modal-backdrop" onMouseDown={onClose}>
    <div className="modal" onMouseDown={(e) => e.stopPropagation()}>
      <div className="topbar" style={{marginBottom: 16}}><h2 style={{margin:0}}>{title}</h2><button className="btn" onClick={onClose}>Закрыть</button></div>
      {children}
    </div>
  </div>
}
