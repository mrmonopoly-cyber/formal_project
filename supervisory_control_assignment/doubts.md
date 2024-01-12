1.	Per qualche ragione (a me) sconosciuta, 
	pur non includendo alcun requisito nell'operazione di merge,
	nell'impianto "controllato" (uso le virgolette perchè senza requisiti non lo si può definire tale) generato 
	vengono impediti movimenti che nell'impianto non controllato sono consentiti.
	La cosa (per me) è strana in quanto un impianto controllato privo di requisiti dovrebbe essere isomorfo a un impianto non controllato (o no?)

	> EDIT: 
	> Il problema era dovuto al fatto che avevamo marcato tutti gli stati dei rover
	> e tutti quelli della batteria (tranne EMPTY).
	> Ciò implicava che la sequenza di eventi accettata
	> prevedesse stati in cui il rover
	> è "quasi" scarico e non si trova in una stazione di ricarica

1.	Il requisito numero 1 non va scritto esplicitamente in quanto l'unico stato marcato di una batteria è FULL.
	L'algoritmo di sintesi si occupa autonomamente della rimozione degli archi (e degli stati) "errati"