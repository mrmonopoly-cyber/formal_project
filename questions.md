# Questions about future project steps

1. We have a right (?) implementation of repeatability checking

	> It should be right as i filled the source code with assertions,
	>
	> whose aim was to check if the output of our implementation
	>
	> was consistent with the output of embedded pynusmv procedures

   This means that we can check repeatability for both members in each couple of base formulas.
   
   > When i say "couple" i mean the couple formed by
	>
	> premise and conclusion formulas of an implication, (each of those without temporal operators)

   But how can we check if repeatability of the premise actually implies repeatability of the conclusion?

   I mean: one could say 

   "Ah okay! I start checking the repeatability for the premise and then

    I distinguish two cases:

    1. If the premise is false the implication holds by classical boolean rules

    1. If the premise if true then I check repeatability of the conclusion and
    
       I state that the implication doesn't hold if and only if the conclusion is not repeatable"

   This is right in most cases, but is not the right choice,

   since there may exist cases such that

   1. premise is repeatable

   1. conclusion is repeatable

   1. there is no implication between repeatability of the premise and repeatability of the conclusion

   > You can easily check this by running a script which adopts the "buggy" strategy
	>
	> and comparing its output whith the outputs of the original scripts

   In conclusion: how the actual fuck do we solve this spicy problem?

1. How do we deal with the fact that a formula and its negation could be both false (or true?)

1. A quanto sembra il nostro algoritmo è corretto, a discapito delle asserzioni non rispettate.

   Quello che facevamo per verificare la correttezza del nostro algoritmo7
   
   era "scomporre" antecedente e conseguente dell'implicazione

   in formule atomiche rimuovendo gli operatori temporali
   
   e quindi asserire che `pynumsv.mc.check_ltl_speck(pynusmv.prop.g(pynusmv.prop.f(spec)))` (con `spec` formula atomica) 

   fosse `True` o `False` a seconda che il nostro algoritmo restituisse `True` o `False`.

   `pynumsv.mc.check_ltl_speck(pynusmv.prop.g(pynusmv.prop.f(spec)))` dovrebbe rappresentare
   
   la proprietà `G F `*spec* ("repeatedly *spec*") ma nonostante ciò le asserzioni fallivano.

   Non sappiamo ancora come mai.

1. Ho scoperto che presso [questo link](https://spot.lre.epita.fr/app/)

   è disponibile un'applicazione web per la generazione di automi di Buchi