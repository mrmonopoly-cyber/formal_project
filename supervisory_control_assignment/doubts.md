1. Per qualche ragione (a me) sconosciuta, 
pur non includendo alcun requisito nell'operazione di merge,
nell'impianto "controllato" (uso le virgolette perchè senza requisiti non lo si può definire tale) generato 
vengono impediti movimenti che nell'impianto non controllato sono consentiti.
La cosa (per me) è strana in quanto un impianto controllato privo di requisiti dovrebbe essere isomorfo a un impianto non controllato (o no?)

1. Il requisito numero 2 potrebbe essere diviso in due (avendo dunque un requisito per rover).
Per esprimere ciascuno dei due requisiti si potrebbe partire da una copia dell'automa di partenza
e tracciare gli eventi di ricarica.
Per esempio se il rover giallo si ricarica prima alla stazione (1,1),
si introduce un secondo insieme di stati,
analogo a quello "standard" ma simbolo del fatto che la ricarica alla stazione (1,1) sia avvenuta.
In tale insieme di stati l'evento di ricarica per lo stato {posizione: (1,1) carica avvenuta: Sì} viene disabilitato.
Se invece il rover giallo si ricarica prima alla stazione (2,4),
si introduce un terzo insieme di stati,
analogo a quello "standard", ma simbolo del fatto che la ricarica alla stazione (2,4) sia avvenuta.
In tale insieme di stati l'evento di ricarica per lo stato {posizione: (2,4) carica avvenuta: Sì} viene disabilitato.
Esempio di transizione: {(1,1), caricati} -> {(1,1,ricarica avvenuta in (1,1)), spostati a destra} -> {(2,1,ricarica avvenuta in (1,1)), ...} -> ...