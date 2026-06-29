import { Background, Controls, ReactFlow } from "@xyflow/react";

const nodes = [
  { id: "1", position: { x: 0, y: 80 }, data: { label: "Alerta crítico" }, type: "input" },
  { id: "2", position: { x: 230, y: 80 }, data: { label: "Regra de automação" } },
  { id: "3", position: { x: 480, y: 80 }, data: { label: "Notificação" }, type: "output" },
];

const edges = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e2-3", source: "2", target: "3" },
];

export function WorkflowsPage() {
  return (
    <section className="space-y-4">
      <div>
        <p className="text-sm text-slate-500">Automações</p>
        <h2 className="text-2xl font-semibold tracking-normal text-white">Fluxos operacionais</h2>
      </div>

      <div className="h-[32rem] overflow-hidden rounded-lg border border-white/10 bg-panel shadow-glow">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background color="#334155" />
          <Controls />
        </ReactFlow>
      </div>
    </section>
  );
}
