/*
 mermaid.js
 It is a Javascript based diagramming and charting tool that renders
 Markdown-inspired text definitions to create and modify diagrams dynamically.
 https://mermaid-js.github.io/mermaid/#/
*/

```mermaid
sequenceDiagram
	participant Manager
	Note over Manager: Input Lattice Basis
	participant Secretary
	participant Worker/s
	participant Pot
	activate Manager
	Manager ->> Manager: Enumeration Tree
	deactivate Manager
	par Share Basic Information<br/>at server's machines
		Manager ->> Secretary: Basic Information<br/>(Lattice-Basis, GSO Coef,<br/>Norms, Range)
		Manager ->> Pot: Procedure Information<br/>(Range, noTasks)
	end
	Secretary ->> Worker/s: Basis Information<br/>(Lattice-Basis, GSO Coef,<br/>Norms, Range)
	loop Tasks Sharing
		Worker/s -->> Manager: I 'm ready<br/>(Connected)
		Manager ->> Worker/s: Task<br/>(starting Vector, Range)
		activate Worker/s
		Worker/s ->> Worker/s: Schnorr and Euchner<br/>Parallel<br/>Enumeration Algorithm
		Worker/s ->> Pot: Task Result<br/>(Shortest Vector)
		deactivate Worker/s
	end
	Manager -->> Manager: Tasks have shared!
	Manager --x Secretary: Close Session
	Pot -->> Pot: Tasks Finished!<br/>I have the Results!
	Note over Pot: Best Shortest<br/>Vector Norm
```