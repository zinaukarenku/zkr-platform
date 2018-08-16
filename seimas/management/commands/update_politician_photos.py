import csv
import re
from io import StringIO
from time import sleep

from django.core.management.base import BaseCommand

from seimas.models import Politician
from seimas.utils import save_image_from_url


class Command(BaseCommand):
    help = 'Update politician photos'

    politicians_csv = """img,name,status
    http://www.lrs.lt/SIPIS/sn_foto/2016/vida_aciene.jpg,VidaAčienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/mantas_adomenas.jpg,MantasAdomėnas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/virgilijus_alekna.jpg,VirgilijusAlekna,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/rimas_andrikis.jpg,RimasAndrikis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/arvydas_anusauskas.jpg,ArvydasAnušauskas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/ausrine_armonaite.jpg,AušrinėArmonaitė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/audronius_azubalis.jpg,AudroniusAžubalis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/valius_azuolas.jpg,ValiusĄžuolas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/kestutis_bacvinka.jpg,KęstutisBacvinka,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/vytautas_bakas.jpg,VytautasBakas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/linas_balsys.jpg,LinasBalsys,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/kestutis_bartkevicius.jpg,KęstutisBartkevičius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/rima_baskiene.jpg,RimaBaškienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/juozas_baublys.jpg,JuozasBaublys,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/antanas_baura.jpg,AntanasBaura,Seimo narys nuo 2017-05-11
    http://www.lrs.lt/SIPIS/sn_foto/2016/juozas_bernatonis.jpg,JuozasBernatonis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/agne_bilotaite.jpg,AgnėBilotaitė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/rasa_budbergyte.jpg,RasaBudbergytė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/valentinas_bukauskas.jpg,ValentinasBukauskas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/guoda_burokiene.jpg,GuodaBurokienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/algirdas_butkevicius.jpg,AlgirdasButkevičius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/petras_cimbaras.jpg,PetrasČimbaras,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/viktorija_cmilyte_nielsen.jpg,ViktorijaČmilytė-Nielsen,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/rimantas_jonas_dagys.jpg,Rimantas JonasDagys,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/irena_degutiene.jpg,IrenaDegutienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/algimantas_dumbrava.jpg,AlgimantasDumbrava,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/justas_dziugelis.jpg,JustasDžiugelis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/aurimas_gaidziunas.jpg,AurimasGaidžiūnas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/vitalijus_gailius.jpg,VitalijusGailius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/dainius_gaizauskas.jpg,DainiusGaižauskas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/arunas_gelunas.jpg,ArūnasGelūnas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/eugenijus_gentvilas.jpg,EugenijusGentvilas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/simonas_gentvilas.jpg,SimonasGentvilas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/kestutis_glaveckas.jpg,KęstutisGlaveckas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/petras_grazulis.jpg,PetrasGražulis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/arunas_gumuliauskas.jpg,ArūnasGumuliauskas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/juozas_imbrasas.jpg,JuozasImbrasas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/stasys_jakeliunas.jpg,StasysJakeliūnas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/jonas_jarutis.jpg,JonasJarutis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/zbignev_jedinskij.jpg,ZbignevJedinskij,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/eugenijus_jovaisa.jpg,EugenijusJovaiša,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/sergejus_jovaisa.jpg,SergejusJovaiša,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/rasa_jukneviciene.jpg,RasaJuknevičienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/vytautas_juozapaitis.jpg,VytautasJuozapaitis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/ricardas_juska.jpg,RičardasJuška,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/vytautas_kamblevicius.jpg,VytautasKamblevičius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/darius_kaminskas.jpg,DariusKaminskas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/ramunas_karbauskis.jpg,RamūnasKarbauskis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/laurynas_kasciunas.jpg,LaurynasKasčiūnas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/dainius_kepenis.jpg,DainiusKepenis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/vytautas_kernagis.jpg,VytautasKernagis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/gintautas_kindurys.jpg,GintautasKindurys,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/gediminas_kirkilas.jpg,GediminasKirkilas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/algimantas_kirkutis.jpg,AlgimantasKirkutis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/vanda_kravcionok.jpg,VandaKravčionok,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/dainius_kreivys.jpg,DainiusKreivys,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/asta_kubiliene.jpg,AstaKubilienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/andrius_kubilius.jpg,AndriusKubilius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/andrius_kupcinskas.jpg,AndriusKupčinskas,Seimo narys nuo 2018-03-10
    http://www.lrs.lt/SIPIS/sn_foto/2016/gabrielius_landsbergis.jpg,GabrieliusLandsbergis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/jonas_liesys.jpg,JonasLiesys,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/linas_antanas_linkevicius.jpg,Linas AntanasLinkevičius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/michal_mackevic.jpg,MichalMackevič,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/mykolas_majauskas.jpg,MykolasMajauskas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/ausra_maldeikiene.jpg,AušraMaldeikienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/bronius_markauskas.jpg,BroniusMarkauskas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/raimundas_martinelis.jpg,RaimundasMartinėlis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/kestutis_masiulis.jpg,KęstutisMasiulis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/bronislovas_matelis.jpg,BronislovasMatelis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/laimute_matkeviciene.jpg,LaimutėMatkevičienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/antanas_matulas.jpg,AntanasMatulas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/kestutis_mazeika.jpg,KęstutisMažeika,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/ruta_miliute.jpg,RūtaMiliūtė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/radvile_morkunaite_mikuleniene.jpg,RadvilėMorkūnaitė-Mikulėnienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/jaroslav_narkevic.jpg,JaroslavNarkevič,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/alfredas_stasys_nauseda.jpg,Alfredas StasysNausėda,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/andrius_navickas.jpg,AndriusNavickas,Seimo narys nuo 2017-06-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/monika_navickiene.jpg,MonikaNavickienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/arvydas_nekrosius.jpg,ArvydasNekrošius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/petras_nevulis.jpg,PetrasNevulis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/ausrine_norkiene.jpg,AušrinėNorkienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/juozas_olekas.jpg,JuozasOlekas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/ceslav_olsevski.jpg,ČeslavOlševski,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/andrius_palionis.jpg,AndriusPalionis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/ausra_papirtiene.jpg,AušraPapirtienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/zygimantas_pavilionis.jpg,ŽygimantasPavilionis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/virgilijus_poderys.jpg,VirgilijusPoderys,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/raminta_popoviene.jpg,RamintaPopovienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/viktoras_pranckietis.jpg,ViktorasPranckietis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/mindaugas_puidokas.jpg,MindaugasPuidokas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/edmundas_pupinis.jpg,EdmundasPupinis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/naglis_puteikis.jpg,NaglisPuteikis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/vytautas_rastenis.jpg,VytautasRastenis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/jurgis_razma.jpg,JurgisRazma,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/juozas_rimkus.jpg,JuozasRimkus,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/viktoras_rinkevicius.jpg,ViktorasRinkevičius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/irina_rozova.jpg,IrinaRozova,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/julius_sabatauskas.jpg,JuliusSabatauskas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/algimantas_salamakinas.jpg,AlgimantasSalamakinas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/paulius_saudargas.jpg,PauliusSaudargas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/valerijus_simulik.jpg,ValerijusSimulik,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/rimantas_sinkevicius.jpg,RimantasSinkevičius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/virginijus_sinkevicius.jpg,VirginijusSinkevičius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/algirdas_sysas.jpg,AlgirdasSysas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/gintare_skaiste.jpg,GintarėSkaistė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/arturas_skardzius.jpg,ArtūrasSkardžius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/saulius_skvernelis.jpg,SauliusSkvernelis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/kestutis_smirnovas.jpg,KęstutisSmirnovas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/lauras_stacevicius.jpg,LaurasStacevičius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/andriejus_stancikas.jpg,AndriejusStančikas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/levute_staniuviene.jpg,LevutėStaniuvienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/kazys_starkevicius.jpg,KazysStarkevičius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/gintaras_steponavicius.jpg,GintarasSteponavičius,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/zenonas_streikus.jpg,ZenonasStreikus,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/algis_strelciunas.jpg,AlgisStrelčiūnas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/dovile_sakaliene.jpg,DovilėŠakalienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/rimante_salaseviciute.jpg,RimantėŠalaševičiūtė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/robertas_sarknickas.jpg,RobertasŠarknickas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/stasys_sedbaras.jpg,StasysŠedbaras,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/irena_siauliene.jpg,IrenaŠiaulienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/audrys_simas.jpg,AudrysŠimas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/ingrida_simonyte.jpg,IngridaŠimonytė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/agne_sirinskiene.jpg,AgnėŠirinskienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/leonard_talmont.jpg,LeonardTalmont,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/rita_tamasuniene.jpg,RitaTamašunienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/tomas_tomilinas.jpg,TomasTomilinas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/stasys_tumenas.jpg,StasysTumėnas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/povilas_urbsys.jpg,PovilasUrbšys,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/gintaras_vaicekauskas.jpg,GintarasVaičekauskas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/ona_valiukeviciute.jpg,OnaValiukevičiūtė,Seimo narė nuo 2018-03-10
    http://www.lrs.lt/SIPIS/sn_foto/2016/petras_valiunas.jpg,PetrasValiūnas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/egidijus_vareikis.jpg,EgidijusVareikis,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/jonas_varkalys.jpg,JonasVarkalys,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/juozas_varzgalys.jpg,JuozasVaržgalys,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/gediminas_vasiliauskas.jpg,GediminasVasiliauskas,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/aurelijus_veryga.jpg,AurelijusVeryga,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/virginija_vingriene.jpg,VirginijaVingrienė,Seimo narė nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/antanas_vinkus.jpg,AntanasVinkus,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/emanuelis_zingeris.jpg,EmanuelisZingeris,Seimo narys nuo 2016-11-14
    http://www.lrs.lt/SIPIS/sn_foto/2016/remigijus_zemaitaitis.jpg,RemigijusŽemaitaitis,Seimo narys nuo 2016-11-14
    """.strip()

    def handle(self, *args, **options):
        csv_reader = csv.reader(StringIO(self.politicians_csv), delimiter=',')
        for row in csv_reader[1:]:
            name_split = re.findall('[A-ZĄČĘĖĮŠŲŪŽ][^A-ZĄČĘĖĮŠŲŪŽ]*', row[1])
            first_name = name_split[0]
            last_name = name_split[1]
            photo_url = row[0].strip()

            politician = Politician.objects.get(first_name__iexact=first_name, last_name__iexact=last_name)

            if not save_image_from_url(politician.photo, photo_url):
                print(f"Unable to save photo of {politician} from url {photo_url}")
            sleep(3)
