/*
 mermaid.js
 It is a Javascript based diagramming and charting tool that renders
 Markdown-inspired text definitions to create and modify diagrams dynamically.
 https://mermaid-js.github.io/mermaid/#/
*/
graph TB
subgraph Server
	Manager[(Manager)] ---> |Info| Secretary(Secretary)
end
Manager ==== |Task| Worker-1st & Worker-2nd & Worker-Nth{{Worker-Nth}}
Secretary -..-> |Info| Worker-1st & Worker-2nd & Worker-Nth
Worker-1st & Worker-2nd & Worker-Nth ---> |Result| Pot[(Pot)]