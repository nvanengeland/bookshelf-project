"""Convert enriched JSON data files to JS data files for the website.
Also adds synopses and fills in missing data from a knowledge base."""
import json
import os

# Knowledge base: synopses, genres, languages, etc. for books where Open Library may lack data
KNOWLEDGE = {
    "Binding 13": {
        "synopsis": "Shannon Lynch belandt op een nieuwe school en trekt de aandacht van Johnny Kavanagh, de sterspeler van het rugbyteam. Een verhaal over eerste liefde, familiegeheimen en de kracht van vertrouwen.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
        "pages": 646,
        "publication_date": 2018,
    },
    "Little Women": {
        "synopsis": "Het tijdloze verhaal van de vier zusjes March - Meg, Jo, Beth en Amy - die opgroeien tijdens de Amerikaanse Burgeroorlog. Een warm verhaal over zusterschap, dromen en volwassen worden.",
        "genre": "Klassiek, Coming-of-age",
        "original_language": "Engels",
    },
    "The Perks of Being a Wallflower": {
        "synopsis": "Charlie, een introverte tiener, begint aan de middelbare school en vindt vriendschap bij de charismatische Sam en Patrick. Een ontroerend verhaal over opgroeien, mentale gezondheid en erbij horen.",
        "genre": "Coming-of-age, Literaire fictie",
        "original_language": "Engels",
    },
    "Iene miene mutte": {
        "synopsis": "Inspecteur Helen Grace jaagt op een seriemoordenaar die zijn slachtoffers kiest via een macaber spelletje. Een donkere, adembenemende thriller.",
        "genre": "Thriller",
        "original_language": "Engels",
    },
    "Girl in Pieces": {
        "synopsis": "Charlotte Davis is zeventien en heeft een verleden vol trauma en zelfbeschadiging. Na een verblijf in een instelling moet ze haar leven weer opbouwen. Een rauw en hoopvol verhaal.",
        "genre": "Young Adult, Literaire fictie",
        "original_language": "Engels",
    },
    "Juniper": {
        "synopsis": "In middeleeuws Engeland groeit het weesmeisje Juniper op bij de wijze vrouw Fillan en leert ze de geheimen van kruiden en magie. Een betoverend fantasyverhaal.",
        "genre": "Fantasy, Historisch",
        "original_language": "Engels",
    },
    "De heksen": {
        "synopsis": "Een jongen en zijn oma ontdekken een geheim genootschap van echte heksen die een duivels plan hebben om alle kinderen van Engeland te veranderen. Griezelig en grappig tegelijk.",
        "genre": "Kinderboek, Fantasy, Humor",
        "original_language": "Engels",
    },
    "Het Pumpkin Spice Café": {
        "synopsis": "Wanneer Dex een charmant café erft in een klein stadje, ontdekt ze dat het runnen van een zaak lastiger is dan verwacht - maar de liefde ligt om de hoek.",
        "genre": "Romantiek, Feel-good",
        "original_language": "Nederlands",
    },
    "It Girl: Team Awkward": {
        "synopsis": "Anna Huntley's leven wordt op z'n kop gezet wanneer haar vader trouwt met een beroemdheid. Plotseling staat ze in de schijnwerpers. Een grappige young adult-roman.",
        "genre": "Humor, Young Adult",
        "original_language": "Engels",
    },
    "FunJungle: Gekidnapt!": {
        "synopsis": "Teddy Fitzroy woont in een enorm dierenpark en raakt betrokken bij het mysterie van een verdwenen koala. Een spannend avontuur voor jonge lezers.",
        "genre": "Avontuur, Mystery, Jeugd",
        "original_language": "Engels",
    },
    "Percy Jackson en de Olympiërs: De bliksemschicht dief": {
        "synopsis": "Percy Jackson ontdekt dat hij de zoon is van Poseidon en wordt beschuldigd van het stelen van Zeus' bliksemschicht. Een episch avontuur door de wereld van de Griekse mythologie.",
        "genre": "Fantasy, Avontuur, Jeugd",
        "original_language": "Engels",
    },
    "De magische apotheek": {
        "synopsis": "Wanneer Ally verhuist, ontdekt ze een geheime apotheek waar magische drankjes worden gebrouwen. Maar er schuilt gevaar achter de betoverende recepten.",
        "genre": "Fantasy, Jeugd",
        "original_language": "Duits",
    },
    "Warrior Cats: De wildernis in": {
        "synopsis": "Huiskat Roosje verlaat zijn comfortabele leven om zich aan te sluiten bij een clan wilde katten in het bos. Het begin van een epische sage vol gevechten en loyaliteit.",
        "genre": "Fantasy, Avontuur, Jeugd",
        "original_language": "Engels",
    },
    "1991": {
        "synopsis": "Een aangrijpend verhaal dat zich afspeelt in België in 1991. Over opgroeien, identiteit en de zoektocht naar wie je bent in een veranderende wereld.",
        "genre": "Literaire fictie, Coming-of-age",
        "original_language": "Nederlands",
    },
    "Echo uit de diepte": {
        "synopsis": "Drie kinderen in drie verschillende tijdperken worden verbonden door een magische mondharmonica. Een meeslepend verhaal over muziek, moed en hoop.",
        "genre": "Historisch, Fantasy, Jeugd",
        "original_language": "Engels",
    },
    "Films die nergens draaien": {
        "synopsis": "Een Vlaamse jongen worstelt met de donkere kant van het internet en de gevolgen voor zijn leven. Een confronterend en actueel jeugdboek.",
        "genre": "Young Adult, Realisme",
        "original_language": "Nederlands",
    },
    "Code Rood": {
        "synopsis": "Een spannend Vlaams jeugdboek over cyberpesten, geheimen en de gevaren van het digitale tijdperk.",
        "genre": "Young Adult, Thriller",
        "original_language": "Nederlands",
    },
    "De Grijze Jager: De ruïnes van Doorn": {
        "synopsis": "Will wordt leerling van de mysterieuze Grijze Jager Halt en leert de geheimen van spionage en overleving in het koninkrijk Doorn. Het begin van een geliefde serie.",
        "genre": "Fantasy, Avontuur",
        "original_language": "Engels",
    },
    "Woodwalkers": {
        "synopsis": "Carag is een gestaltverwisselaar die kan veranderen tussen mens en poema. Op een speciale school leert hij omgaan met zijn dubbele identiteit.",
        "genre": "Fantasy, Avontuur, Jeugd",
        "original_language": "Duits",
    },
    "Harry Potter en de Steen der Wijzen": {
        "synopsis": "De elfjarige Harry Potter ontdekt dat hij een tovenaar is en begint aan Zweinsteins Hogeschool voor Hekserij en Hocus-Pocus, waar een groot avontuur op hem wacht.",
        "genre": "Fantasy, Avontuur",
        "original_language": "Engels",
    },
    "Geen beste dag voor voodoo": {
        "synopsis": "Een hilarisch en griezelig verhaal waarin een tiener per ongeluk een voodoo-pop activeert met desastreuze gevolgen. Humor en horror in perfecte balans.",
        "genre": "Humor, Horror, Young Adult",
        "original_language": "Engels",
    },
    "Dumplin'": {
        "synopsis": "Willowdean 'Dumplin'' Dickson, een zelfverzekerd meisje met een maatje meer, schrijft zich in voor de lokale missverkiezing om een statement te maken. Een feelgood-verhaal over zelfacceptatie.",
        "genre": "Young Adult, Romantiek, Humor",
        "original_language": "Engels",
    },
    "X-Scape": {
        "synopsis": "Een razendspannend Vlaams jeugdboek vol escaperoomsituaties en puzzels. Kun je ontsnappen voor de tijd op is?",
        "genre": "Thriller, Avontuur, Jeugd",
        "original_language": "Nederlands",
    },
    "Sunrise on the Reaping": {
        "synopsis": "Een prequel op The Hunger Games die het verhaal vertelt van de Tweede Kwartskwelling - de 50ste Hongerspelen waarin Haymitch Abernathy deelnam.",
        "genre": "Sciencefiction, Dystopie, Young Adult",
        "original_language": "Engels",
        "publication_date": 2025,
    },
    "De Zeven Zussen": {
        "synopsis": "Zes geadopteerde zussen gaan elk op reis om hun afkomst te ontdekken na de dood van hun vader. Een meeslepende familiesaga die de hele wereld rondreist.",
        "genre": "Romantiek, Historisch, Familiesaga",
        "original_language": "Engels",
    },
    "Mythos": {
        "synopsis": "Stephen Fry vertelt de Griekse mythen na op een moderne, humoristische en meeslepende manier. Van de schepping tot de helden van de Olympus.",
        "genre": "Mythologie, Non-fictie",
        "original_language": "Engels",
    },
    "Helden": {
        "synopsis": "Het vervolg op Mythos waarin Stephen Fry de heldenverhalen uit de Griekse mythologie hervertelt: Perseus, Heracles, Theseus en meer.",
        "genre": "Mythologie, Non-fictie",
        "original_language": "Engels",
    },
    "Surrounded by Narcissists": {
        "synopsis": "Thomas Erikson legt uit hoe je narcisten herkent in je omgeving en hoe je ermee omgaat. Praktisch en toegankelijk geschreven.",
        "genre": "Psychologie, Non-fictie",
        "original_language": "Zweeds",
    },
    "Dir-Yak Omnibus I": {
        "synopsis": "Een verzameling avontuurlijke stripverhalen van Dir-Yak, vol humor en actie.",
        "genre": "Strip, Avontuur, Humor",
        "original_language": "Nederlands",
    },
    "Supernerd of Topmodel": {
        "synopsis": "Een tiener worstelt met de keuze tussen haar nerdy passies en de populaire wereld van mode. Een grappig en herkenbaar verhaal.",
        "genre": "Young Adult, Humor",
        "original_language": "Engels",
    },
    "De trein van vier over twaalf": {
        "synopsis": "Vier kinderen in het naoorlogse Parijs vinden een brief die hen op een mysterieus avontuur stuurt. Een sfeervolle, warme roman.",
        "genre": "Jeugd, Avontuur, Historisch",
        "original_language": "Frans",
    },
    "The Hunger Games": {
        "synopsis": "In een dystopische toekomst wordt de zestienjarige Katniss Everdeen geselecteerd om deel te nemen aan de Hongerspelen - een televisie-evenement waarbij tieners tot de dood moeten vechten.",
        "genre": "Sciencefiction, Dystopie, Young Adult",
        "original_language": "Engels",
    },
    "De laatste dochter": {
        "synopsis": "Een meeslepende Nederlandstalige thriller over familiegeheimen, verraad en de zoektocht naar de waarheid over een verdwenen vrouw.",
        "genre": "Thriller, Mysterie",
        "original_language": "Nederlands",
    },
    "Five Survive": {
        "synopsis": "Zes vrienden zitten vast in een camper terwijl een schutter hen onder schot houdt. Een van hen verbergt een geheim. Een claustrofobische pageturner.",
        "genre": "Thriller, Young Adult",
        "original_language": "Engels",
    },
    "Percy Jackson en de Olympiërs": {
        "synopsis": "De complete serie over Percy Jackson, halfgod en zoon van Poseidon, die epische avonturen beleeft in een wereld waar de Griekse mythologie springlevend is.",
        "genre": "Fantasy, Avontuur, Jeugd",
        "original_language": "Engels",
    },
    "The Cruel Prince": {
        "synopsis": "Jude werd als kind ontvoerd naar het rijk van de feeën. Om te overleven moet ze de wreedste prins van allemaal zien te slim af zijn. Duistere fantasy vol intriges.",
        "genre": "Fantasy, Young Adult",
        "original_language": "Engels",
    },
    "Once Upon a Broken Heart": {
        "synopsis": "Evangeline sluit een deal met de mysterieuze Prins der Harten om haar liefde terug te winnen. Maar elke wens heeft een prijs. Betoverend en romantisch.",
        "genre": "Fantasy, Romantiek",
        "original_language": "Engels",
    },
    "Obsidian (Lux serie)": {
        "synopsis": "Katy verhuist naar een klein stadje en ontdekt dat haar knappe buurman Daemon een buitenaards wezen is. Het begin van een explosieve serie vol actie en romantiek.",
        "genre": "Sciencefiction, Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "Talon": {
        "synopsis": "Ember is een draak die als mens leeft. Wanneer ze verliefd wordt op een drakenjager, moet ze kiezen tussen haar hart en haar soort.",
        "genre": "Fantasy, Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "From Blood and Ash": {
        "synopsis": "Poppy is haar hele leven beschermd geweest als de Maagd. Maar wanneer ze de mysterieuze Hawke ontmoet, komt ze erachter dat alles wat ze kent een leugen is.",
        "genre": "Fantasy, Romantiek",
        "original_language": "Engels",
    },
    "Shatter Me (Alizeh serie)": {
        "synopsis": "Juliette heeft een dodelijke aanraking en wordt opgesloten. Wanneer ze bevrijd wordt, moet ze kiezen: wapen zijn of strijden voor vrijheid.",
        "genre": "Sciencefiction, Dystopie, Romantiek",
        "original_language": "Engels",
    },
    "When It's Real": {
        "synopsis": "Oakley krijgt een aanbod om de nep-vriendin te spelen van popster Vaughn. Wat begint als een zakelijke deal, wordt al snel echte gevoelens.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "De Hongerspelen": {
        "synopsis": "De Nederlandse vertaling van The Hunger Games. Katniss Everdeen neemt de plaats in van haar zusje in de dodelijke Hongerspelen.",
        "genre": "Sciencefiction, Dystopie, Young Adult",
        "original_language": "Engels",
    },
    "Schaduw van de Vos": {
        "synopsis": "In een door Japanse mythologie geïnspireerde wereld moet Yumeko, half mens en half vos, een krachtig artefact beschermen tegen duistere machten.",
        "genre": "Fantasy, Avontuur",
        "original_language": "Engels",
    },
    "De Kinderen van Orpheus": {
        "synopsis": "Een Nederlandstalige fantasyserie vol mythologie, magie en avontuur. De kinderen van Orpheus ontdekken hun bijzondere krachten.",
        "genre": "Fantasy, Jeugd",
        "original_language": "Nederlands",
    },
    "Zeis": {
        "synopsis": "In een toekomst zonder dood zijn Zeisen de enigen die mogen beslissen wie sterft. Twee leerling-Zeisen ontdekken de duistere waarheid achter hun roeping.",
        "genre": "Sciencefiction, Dystopie, Young Adult",
        "original_language": "Engels",
    },
    "You'd Be Home Now": {
        "synopsis": "Na een auto-ongeluk probeert Emory haar broer te helpen met zijn verslaving, terwijl ze zelf worstelt met haar plek in de wereld.",
        "genre": "Young Adult, Realisme",
        "original_language": "Engels",
    },
    "Royals": {
        "synopsis": "Ella Harper wordt verliefd op een rijke erfgenaam en belandt in een wereld van luxe, geheimen en familiedrama's.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "No Exit": {
        "synopsis": "Een spannend Nederlandstalig jeugdboek van Maren Stoffels over een groep tieners die vast komt te zitten in een beangstigende situatie.",
        "genre": "Thriller, Young Adult",
        "original_language": "Nederlands",
    },
    "Doodleuk": {
        "synopsis": "De Nederlandse vertaling van 'A Good Girl's Guide to Murder'. Pip onderzoekt een vijf jaar oude moordzaak voor haar eindproject.",
        "genre": "Thriller, Mystery, Young Adult",
        "original_language": "Engels",
    },
    "The Maze Runner": {
        "synopsis": "Thomas wordt wakker in een lift zonder herinneringen. Hij belandt in de Glade, omringd door een gigantisch doolhof vol dodelijke gevaren.",
        "genre": "Sciencefiction, Dystopie, Young Adult",
        "original_language": "Engels",
    },
    "If He Had Been with Me": {
        "synopsis": "Autumn en Finny waren ooit beste vrienden. Een hartverscheurend verhaal over gemiste kansen, eerste liefde en het lot.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "Gebroken": {
        "synopsis": "Een psychologische thriller van Mel Wallis de Vries over een meisje dat ontdekt dat niemand is wie hij lijkt te zijn.",
        "genre": "Thriller, Young Adult",
        "original_language": "Nederlands",
    },
    "I Wish You Would": {
        "synopsis": "Een romantisch verhaal over tweede kansen en de moed om je hart te volgen, ondanks alles wat er eerder is gebeurd.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "Een vloek zo eenzaam": {
        "synopsis": "De Nederlandse vertaling van 'A Curse So Dark and Lonely'. Prins Rhen is gevangen in een vloek en alleen Harper kan hem redden.",
        "genre": "Fantasy, Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "Powerless": {
        "synopsis": "In een wereld waar iedereen superkrachten heeft, is Paedyn de enige zonder. Wanneer ze de aandacht trekt van de kroonprins, begint een dodelijk spel.",
        "genre": "Fantasy, Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "Thieves' Gambit": {
        "synopsis": "Ross komt uit een familie van meesterdieven. Wanneer ze deelneemt aan een dodelijke wedstrijd, moet ze alles riskeren om te winnen.",
        "genre": "Avontuur, Thriller, Young Adult",
        "original_language": "Engels",
    },
    "De duistere profetie": {
        "synopsis": "De Nederlandse vertaling van een deel uit de Shatter Me-serie van Tahereh Mafi. Een dystopische wereld vol actie en romantiek.",
        "genre": "Sciencefiction, Dystopie, Romantiek",
        "original_language": "Engels",
    },
    "Check & Mate": {
        "synopsis": "Mallory wordt teruggetrokken in de schaakwereld wanneer ze een grootmeester verslaat. Een slimme romantische komedie in de competitieve schaakscene.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "The Fault in Our Stars": {
        "synopsis": "Hazel en Augustus, twee tieners met kanker, vallen voor elkaar en delen een onvergetelijke reis naar Amsterdam. Hartverscheurend en hoopvol tegelijk.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "Kleine Gelukjes": {
        "synopsis": "Een warm en luchtig Nederlandstalig boek over de kleine dingen in het leven die het verschil maken. Feel-good en inspirerend.",
        "genre": "Feel-good, Romantiek",
        "original_language": "Nederlands",
    },
    "Schaduwliefde": {
        "synopsis": "De Nederlandse vertaling van een roman van Ruta Sepetys. Een historisch verhaal over verboden liefde en overleven in donkere tijden.",
        "genre": "Historisch, Romantiek",
        "original_language": "Engels",
    },
    "IJzerkop": {
        "synopsis": "Het waargebeurde verhaal van Louise de Bettignies, een Vlaamse spionne in de Eerste Wereldoorlog. Een indrukwekkende historische roman van Jean-Claude Van Rijckeghem.",
        "genre": "Historisch, Avontuur",
        "original_language": "Nederlands",
    },
    "One Golden Summer": {
        "synopsis": "Een onverwachte zomerliefde die alles verandert. Een warm en emotioneel verhaal over verlies, genezing en nieuwe kansen.",
        "genre": "Romantiek",
        "original_language": "Engels",
    },
    "The Maidens": {
        "synopsis": "Groepstherapeutisch Mariana vermoedt dat een charismatische professor aan Cambridge betrokken is bij een reeks moorden op studentes. Een literaire thriller.",
        "genre": "Thriller, Mystery",
        "original_language": "Engels",
    },
    "Say You'll Remember Me": {
        "synopsis": "De Nederlandse titel voor een boek van Abby Jimenez, een romantische komedie vol humor en warmte.",
        "genre": "Romantiek",
        "original_language": "Engels",
    },
    "Heart Bones": {
        "synopsis": "Beyah heeft een moeilijk leven achter zich. Tijdens een zomer bij haar afwezige vader ontmoet ze Samson, en ontdekt ze wat het betekent om lief te hebben.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "How to Kill Men and Get Away with It": {
        "synopsis": "Socialite Kitty Collins vermoordt per ongeluk een man en ontdekt dat ze er een talent voor heeft. Een donkere, feministische komedie.",
        "genre": "Thriller, Humor, Satire",
        "original_language": "Engels",
    },
    "Better Than the Movies": {
        "synopsis": "Liz is dol op romcoms en probeert de perfecte filmromance te creëren met haar crush. Maar haar irritante buurman Wes gooit roet in het eten.",
        "genre": "Romantiek, Young Adult, Humor",
        "original_language": "Engels",
    },
    "Mr Wrong Number": {
        "synopsis": "Olivia stuurt per ongeluk een pikant berichtje naar het verkeerde nummer. De ontvanger blijkt haar vervelende huisgenoot te zijn.",
        "genre": "Romantiek, Humor",
        "original_language": "Engels",
    },
    "The Housemaid": {
        "synopsis": "Millie wordt huishoudster bij de perfecte familie Winchester. Maar achter de gesloten deuren schuilt een duister geheim.",
        "genre": "Thriller, Mystery",
        "original_language": "Engels",
    },
    "The Seven Husbands of Evelyn Hugo": {
        "synopsis": "De legendarische filmster Evelyn Hugo onthult eindelijk het verhaal achter haar zeven huwelijken en haar grote, verboden liefde.",
        "genre": "Historisch, Romantiek, Literaire fictie",
        "original_language": "Engels",
    },
    "The Perfect Marriage": {
        "synopsis": "Sarah Morgan is advocate en verdedigt haar eigen man, die beschuldigd wordt van moord op zijn minnares. Maar wie liegt er eigenlijk?",
        "genre": "Thriller, Mystery",
        "original_language": "Engels",
    },
    "A Thousand Boy Kisses": {
        "synopsis": "Rune en Poppy zijn zielsverwanten sinds hun kindertijd. Maar het lot heeft andere plannen. Een hartverscheurend liefdesverhaal.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "The Murder After the Night Before": {
        "synopsis": "Na een wilde avond wordt een vrouw wakker met bloed aan haar handen en geen herinneringen. Een spannende whodunit met een twist.",
        "genre": "Thriller, Mystery, Humor",
        "original_language": "Engels",
    },
    "When in Rome": {
        "synopsis": "Amelia ontmoet de chagrijnige Noah in een klein stadje en ontdekt dat achter zijn norse buitenkant een warm hart schuilgaat.",
        "genre": "Romantiek",
        "original_language": "Engels",
    },
    "Malibu Rising": {
        "synopsis": "De Riva-familie geeft hun legendarische zomerfeest in Malibu in 1983. Tegen het einde van de avond staat het huis in brand. Een familiesaga vol geheimen.",
        "genre": "Historisch, Literaire fictie",
        "original_language": "Engels",
    },
    "The Reappearance of Rachel Price": {
        "synopsis": "Bel's moeder verdween achttien jaar geleden. Nu keert ze plotseling terug. Maar is ze echt wie ze zegt te zijn?",
        "genre": "Thriller, Mystery, Young Adult",
        "original_language": "Engels",
    },
    "A Good Girl's Guide to Murder": {
        "synopsis": "Pip onderzoekt een vijf jaar oude moordzaak voor haar eindproject. Maar hoe dieper ze graaft, hoe gevaarlijker het wordt.",
        "genre": "Thriller, Mystery, Young Adult",
        "original_language": "Engels",
    },
    "Letters to the Lost": {
        "synopsis": "Juliet en Declan schrijven anonieme brieven naar elkaar op een begraafplaats. Zonder te weten wie de ander is, worden ze elkaars reddingsboei.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "Before We Were Strangers": {
        "synopsis": "Matt en Grace waren elkaars grote liefde op de universiteit. Vijftien jaar later kruisen hun paden opnieuw.",
        "genre": "Romantiek",
        "original_language": "Engels",
    },
    "Anna and the French Kiss": {
        "synopsis": "Anna wordt naar een kostschool in Parijs gestuurd en wordt verliefd op de charmante Étienne St. Clair. Een zoete romcom in de Stad van de Liefde.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "The Girl on the Train": {
        "synopsis": "Rachel neemt elke dag de trein en ziet een 'perfect' koppel vanuit het raam. Tot ze iets schokkends ziet. Een psychologische thriller.",
        "genre": "Thriller, Mystery",
        "original_language": "Engels",
    },
    "Until Friday Night": {
        "synopsis": "West heeft een geheim dat hem verscheurt. Maggie spreekt niet meer. Samen vinden ze troost en misschien wel liefde.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "The Way I Used to Be": {
        "synopsis": "Eden wordt aangerand door de beste vriend van haar broer. Het boek volgt haar vier jaar op de middelbare school terwijl ze worstelt met het trauma.",
        "genre": "Young Adult, Realisme",
        "original_language": "Engels",
    },
    "Throttled": {
        "synopsis": "Maya staat te popelen als ze de kans krijgt om voor een Formule 1-team te werken. Maar coureur Noah Slade maakt het haar niet makkelijk - tot de spanning omslaat in passie.",
        "genre": "Romantiek",
        "original_language": "Engels",
    },
    "Regretting You": {
        "synopsis": "Morgan en haar tienerdochter Clara worden uit elkaar gedreven door een familietragedie en ontdekken allebei schokkende geheimen.",
        "genre": "Romantiek, Familiedrama",
        "original_language": "Engels",
    },
    "November 9": {
        "synopsis": "Fallon en Ben ontmoeten elkaar elk jaar op 9 november. Een verhaal over liefde, vertrouwen en de vraag: is hun relatie echt of fictie?",
        "genre": "Romantiek",
        "original_language": "Engels",
    },
    "Every Last Word": {
        "synopsis": "Samantha lijdt aan OCS en verbergt dit voor haar populaire vriendinnen. Wanneer ze een geheime poëzieclub ontdekt, vindt ze eindelijk haar echte zelf.",
        "genre": "Young Adult, Realisme",
        "original_language": "Engels",
    },
    "Heartstopper Volume 1": {
        "synopsis": "Charlie en Nick zitten naast elkaar in de klas. Charlie is verliefd, maar Nick is populair en hetero... toch? Een schattige graphic novel over eerste liefde.",
        "genre": "Graphic Novel, Romantiek, LGBTQ+",
        "original_language": "Engels",
    },
    "Solitaire": {
        "synopsis": "Tori Spring observeert het leven liever vanaf de zijlijn. Maar wanneer een mysterieuze groep genaamd Solitaire de school saboteert, kan ze niet langer toekijken.",
        "genre": "Young Adult, Realisme",
        "original_language": "Engels",
    },
    "Radio Silence": {
        "synopsis": "Frances en Aled ontdekken dat ze allebei fan zijn van dezelfde podcast. Een verhaal over vriendschap, identiteit en de druk om te presteren.",
        "genre": "Young Adult, Realisme",
        "original_language": "Engels",
    },
    "I Was Born for This": {
        "synopsis": "Angel is superfan van boyband The Ark. Jimmy is het angstige gezicht van de band. Wanneer hun werelden botsen, verandert alles.",
        "genre": "Young Adult, Realisme",
        "original_language": "Engels",
    },
    "Loveless": {
        "synopsis": "Georgia gaat naar de universiteit en ontdekt dat ze aromantisch en aseksueel is. Een belangrijk en warm verhaal over zelfontdekking en vriendschap.",
        "genre": "Young Adult, LGBTQ+, Coming-of-age",
        "original_language": "Engels",
    },
    "Red, White & Royal Blue": {
        "synopsis": "Alex, de zoon van de Amerikaanse presidente, en Prins Henry van Engeland worden verliefd. Een romantische komedie met politieke intriges.",
        "genre": "Romantiek, LGBTQ+, Humor",
        "original_language": "Engels",
    },
    "Lang leve Jane": {
        "synopsis": "Een humoristische hervertelling van Jane Eyre, waarin Jane ontdekt dat ze bijzondere gaven heeft. Vol humor en avontuur.",
        "genre": "Fantasy, Humor, Young Adult",
        "original_language": "Engels",
    },
    "Lily": {
        "synopsis": "Een Vlaamse roman van Tom de Cock over Lily en haar zoektocht naar zichzelf. Gevoelig en eerlijk geschreven.",
        "genre": "Young Adult, Realisme",
        "original_language": "Nederlands",
    },
    "Storm": {
        "synopsis": "Een Vlaamse roman van Tom de Cock. Een intense en emotionele coming-of-age.",
        "genre": "Young Adult, Realisme",
        "original_language": "Nederlands",
    },
    "Maxton Hall College": {
        "synopsis": "Ruby krijgt een beurs voor de elite-school Maxton Hall. Daar botst ze met de arrogante James Beaufort, maar de spanning tussen hen is niet te ontkennen.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Duits",
    },
    "CTRL-A": {
        "synopsis": "Een Nederlandstalig jeugdboek over een meisje dat alles wil controleren in haar leven, maar ontdekt dat loslaten soms de enige optie is.",
        "genre": "Young Adult, Realisme",
        "original_language": "Nederlands",
    },
    "Dit mag niemand weten": {
        "synopsis": "Een aangrijpend Nederlandstalig verhaal over een geheim dat een tiener met zich meedraagt en de gevolgen wanneer de waarheid aan het licht komt.",
        "genre": "Young Adult, Realisme",
        "original_language": "Nederlands",
    },
    "De roep van het hart": {
        "synopsis": "De Nederlandse vertaling van 'The Selection' van Kiera Cass. 35 meisjes strijden om het hart van prins Maxon in een dystopische toekomst.",
        "genre": "Romantiek, Dystopie, Young Adult",
        "original_language": "Engels",
    },
    "People We Meet on Vacation": {
        "synopsis": "Alex en Poppy zijn al jaren beste vrienden en gaan elk jaar samen op vakantie. Tot twee jaar geleden iets misging. Kunnen ze hun vriendschap redden?",
        "genre": "Romantiek",
        "original_language": "Engels",
    },
    "The Bodyguard": {
        "synopsis": "Hannah is lijfwacht en moet de charmante acteur Jack beschermen. Doen alsof ze een stel zijn maakt het er niet makkelijker op.",
        "genre": "Romantiek, Humor",
        "original_language": "Engels",
    },
    "A Thousand Broken Pieces": {
        "synopsis": "Het vervolg op A Thousand Boy Kisses. Een emotioneel verhaal over verlies, genezing en de kracht van liefde die verder reikt dan het leven.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "Picking Daisies on a Sunday": {
        "synopsis": "Een romantisch verhaal over liefde, verlies en het vinden van schoonheid in het alledaagse.",
        "genre": "Romantiek",
        "original_language": "Engels",
    },
    "Moordgids voor lieve meisjes": {
        "synopsis": "De Nederlandse vertaling van 'A Good Girl's Guide to Murder'. Pip onderzoekt een oude moordzaak en komt dichter bij de waarheid dan veilig is.",
        "genre": "Thriller, Mystery, Young Adult",
        "original_language": "Engels",
    },
    "Onderstroom": {
        "synopsis": "Een Vlaamse thriller van Goedele Ghijsen. Een spannend verhaal over geheimen die onder de oppervlakte borrelen.",
        "genre": "Thriller",
        "original_language": "Nederlands",
    },
    "Een lied voor Achilles": {
        "synopsis": "De Nederlandse vertaling van 'The Song of Achilles'. Het verhaal van de Trojaanse Oorlog verteld door de ogen van Patroclus, de geliefde van Achilles.",
        "genre": "Historisch, Mythologie, LGBTQ+",
        "original_language": "Engels",
    },
    "De kleuren van magie": {
        "synopsis": "De Nederlandse vertaling van 'A Darker Shade of Magic'. Kell reist tussen parallelle versies van Londen en raakt betrokken bij een gevaarlijk complot.",
        "genre": "Fantasy",
        "original_language": "Engels",
    },
    "List & Leugens": {
        "synopsis": "De Nederlandse vertaling van 'Six of Crows'. Zes buitenbeentjes plannen de onmogelijkste overval ooit in een wereld vol magie en gevaar.",
        "genre": "Fantasy, Avontuur",
        "original_language": "Engels",
    },
    "Het grote misschien": {
        "synopsis": "De Nederlandse vertaling van 'Looking for Alaska'. Miles gaat naar een kostschool en ontmoet de mysterieuze Alaska Young, die zijn wereld op z'n kop zet.",
        "genre": "Young Adult, Coming-of-age",
        "original_language": "Engels",
    },
    "Aristoteles & Dante ontdekken de geheimen van het universum": {
        "synopsis": "Twee Mexicaans-Amerikaanse tieners ontdekken vriendschap, familie en de kracht van liefde in een prachtig geschreven coming-of-age roman.",
        "genre": "Young Adult, LGBTQ+, Coming-of-age",
        "original_language": "Engels",
    },
    "Op het einde gaan ze allebei dood": {
        "synopsis": "De Nederlandse vertaling van 'They Both Die at the End'. Mateo en Rufus krijgen te horen dat ze vandaag sterven. Ze besluiten elkaars laatste dag bijzonder te maken.",
        "genre": "Young Adult, Sciencefiction, LGBTQ+",
        "original_language": "Engels",
    },
    "Shakespeare kent me beter dan mijn lief": {
        "synopsis": "Een Nederlandstalig boek over liefde, literatuur en de vraag of fictieve personages ons soms beter begrijpen dan echte mensen.",
        "genre": "Non-fictie, Literatuur",
        "original_language": "Nederlands",
    },
    "5 stappen van jou": {
        "synopsis": "De Nederlandse vertaling van 'Five Feet Apart'. Stella en Will zijn allebei patiënt met taaislijmziekte en mogen niet te dicht bij elkaar komen. Maar de liefde kent geen grenzen.",
        "genre": "Romantiek, Young Adult",
        "original_language": "Engels",
    },
    "Het parfum": {
        "synopsis": "Jean-Baptiste Grenouille wordt geboren met een bovenmenselijke reukzin in het 18e-eeuwse Parijs. Zijn obsessie met de perfecte geur leidt tot moord. Een literaire klassieker.",
        "genre": "Literaire fictie, Historisch, Thriller",
        "original_language": "Duits",
    },
}

def merge_data(enriched, knowledge):
    """Merge Open Library data with knowledge base. Knowledge base always wins."""
    VALID_LANGS = {"Engels", "Nederlands", "Frans", "Duits", "Zweeds", "Spaans"}

    for book in enriched:
        title = book["title"]
        kb = knowledge.get(title, {})

        # Synopsis: always prefer knowledge base
        if kb.get("synopsis"):
            book["synopsis"] = kb["synopsis"]
        elif not book.get("synopsis"):
            book["synopsis"] = ""

        # Genre: knowledge base wins, or keep OL data if valid
        if kb.get("genre"):
            book["genre"] = kb["genre"]
        elif not book.get("genre"):
            book["genre"] = "Fictie"

        # Language: knowledge base wins; fix invalid OL languages
        if kb.get("original_language"):
            book["original_language"] = kb["original_language"]
        elif book.get("original_language") and book["original_language"] not in VALID_LANGS:
            book["original_language"] = ""

        # Pages: knowledge base fills gaps
        if kb.get("pages") and not book.get("pages"):
            book["pages"] = kb["pages"]

        # Publication date: knowledge base fills gaps
        if kb.get("publication_date") and not book.get("publication_date"):
            book["publication_date"] = kb["publication_date"]

    return enriched


def load_missing_data(data_dir):
    """Load additional data from all_missing.json."""
    missing_file = os.path.join(data_dir, "all_missing.json")
    if os.path.exists(missing_file):
        with open(missing_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def apply_missing_data(enriched, missing):
    """Apply missing data (covers, ISBNs, pages, years) to enriched books."""
    for book in enriched:
        title = book["title"]
        if title in missing:
            md = missing[title]
            if md.get("cover_front") and not book.get("cover_front"):
                book["cover_front"] = md["cover_front"]
            if md.get("isbn") and not book.get("isbn"):
                book["isbn"] = md["isbn"]
            if md.get("pages") and not book.get("pages"):
                book["pages"] = md["pages"]
            if md.get("publication_date") and not book.get("publication_date"):
                book["publication_date"] = md["publication_date"]
    return enriched


def load_publishers(data_dir):
    """Load publisher data from publishers.json."""
    pub_file = os.path.join(data_dir, "publishers.json")
    if os.path.exists(pub_file):
        with open(pub_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_synopses(data_dir):
    """Load synopses from synopses batch files.
    Handles keys that may be 'Title' or 'Title - Author'."""
    synopses = {}
    import glob
    for f in sorted(glob.glob(os.path.join(data_dir, "synopses_batch*.json"))):
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            for key, val in data.items():
                # Normalize key: strip " - Author" suffix if present
                title = key.split(" - ")[0].strip() if " - " in key else key
                # Keep longest synopsis if duplicate
                if title not in synopses or len(val) > len(synopses.get(title, "")):
                    synopses[title] = val
    return synopses


def apply_publishers(enriched, publishers):
    """Add publisher field to books."""
    for book in enriched:
        if book["title"] in publishers:
            book["publisher"] = publishers[book["title"]]
        elif not book.get("publisher"):
            book["publisher"] = ""
    return enriched


def apply_synopses(enriched, synopses):
    """Override synopses with web-sourced ones (longer = better)."""
    for book in enriched:
        web_syn = synopses.get(book["title"], "")
        if web_syn and len(web_syn) > len(book.get("synopsis", "")):
            book["synopsis"] = web_syn
    return enriched


def main():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    missing = load_missing_data(data_dir)
    publishers = load_publishers(data_dir)
    synopses = load_synopses(data_dir)

    for grade, var_name in [("graad_1", "GRAAD_1_DATA"), ("graad_2", "GRAAD_2_DATA"), ("graad_3", "GRAAD_3_DATA")]:
        input_file = os.path.join(data_dir, f"{grade}_enriched.json")

        if not os.path.exists(input_file):
            print(f"WARNING: {input_file} not found, skipping {grade}")
            continue

        with open(input_file, "r", encoding="utf-8") as f:
            enriched = json.load(f)

        # Apply all data layers
        enriched = apply_missing_data(enriched, missing)
        merged = merge_data(enriched, KNOWLEDGE)
        merged = apply_publishers(merged, publishers)
        merged = apply_synopses(merged, synopses)

        # Write JS file
        js_file = os.path.join(data_dir, f"{grade}.js")
        with open(js_file, "w", encoding="utf-8") as f:
            f.write(f"const {var_name} = ")
            json.dump(merged, f, ensure_ascii=False, indent=2)
            f.write(";\n")

        print(f"{grade}: {len(merged)} books -> {js_file}")


if __name__ == "__main__":
    main()
