from bs4 import BeautifulSoup, Tag
from utils.tableParser import tableParser

tableParser = tableParser()
parsedTables = {}

def parseTables(soup):
    for table in soup.findAll('table'):
        parsedTable = tableParser.toJson(table)
        h = hash(str(parsedTable))
        parsedTables[h] = parsedTable
        table.replaceWith('parsedTable#' + str(h))

    return soup

testDocument = """
    <div class="data">
    <!-- Affiche plus d'info si possible -->
    <!-- Affiche ou masque les informations sur le texte-->
    <div hidden="true" style="visibility:hidden;height:0px;">
    <h3>Informations sur ce texte</h3>
    <div>
    <!-- Lien sur la transposition eurlex -->
    <!-- Gestion des liens TRANSPOSITION -->
    <!-- Gestion des liens d'application des textes autres que directives -->
    <!-- Gestion des liens D'APPLICATION -->
    <!-- RESUME -->
    <!--  MOTS-CLES -->
    <!-- RECTIFICATIF -->
    <!-- DOSSIERS LEGISLATIFS -->
    <!-- OBSERVATION -->
    <!--  LIENS ANTERIEURS -->
    <!--  LIENS POSTERIEURS -->
    </div>
    <br>
    <hr>
    <br>
    </div>
    <div>
    <div class="enteteTexte">
    <span>
    <span class="published_in" about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/html" property="eli:published_in" content="https://www.legifrance.gouv.fr/eli/jo/2017/12/6/fr/html"></span>
    <span>JORF n°0284 du 6 décembre 2017</span>
    <br>
    texte n° 15
    </span>
    <span about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo" property="eli:date_publication" datatype="xsd:date" content="2017-12-06"></span>
    <span property="eli:type_document" content="ARRETE"></span>
    <br>
    <br>
    <br>
    <br>
    <span>
    <strong>Arrêté du <span property="eli:date_document" datatype="xsd:date" content="2017-11-24">24 novembre 2017</span> modifiant la liste des spécialités pharmaceutiques agréées à l'usage des collectivités et divers services publics</strong>
    </span>
    <br>
    <br>
    NOR:  <span property="eli:id_local">SSAS1731442A</span>
    <div class="enteteTexteELI">
    ELI: https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte
    </div>
    </div><!-- end entete -->
    <div>
    <div>
    </div><!-- end notice -->
    <div>
    <p align="left">
    <br>La ministre des solidarités et de la santé et le ministre de l'action et des comptes publics,<br>Vu le <a href="/affichCode.do?cidTexte=LEGITEXT000006072665&amp;dateTexte=29990101&amp;categorieLien=cid" rel="eli:cites">code de la santé publique</a>, notamment ses articles L. 5123-2, L. 5123-3 et D. 5123-4 ;<br>Vu le <a href="/affichCode.do?cidTexte=LEGITEXT000006073189&amp;dateTexte=29990101&amp;categorieLien=cid" rel="eli:cites">code de la sécurité sociale</a> ;<br>Vu le <a href="/affichCode.do?cidTexte=LEGITEXT000006069577&amp;dateTexte=29990101&amp;categorieLien=cid" rel="eli:cites">code général des impôts</a>, notamment l'article 281 octies ;<br>Vu les avis de la Commission de la transparence en date du 17 mai 2017 et 5 juillet 2017,<br>Arrêtent :</p>
    </div><!-- end visas -->
    <div> <!-- Content -->
    <a style="text-decoration: none;" id="JORFARTI000036150830" name="JORFARTI000036150830"> </a><div class="article">
    <div class="titreArt">Article 1</div>
    <p>
    <br>La liste des spécialités pharmaceutiques agréées à l'usage des collectivités et divers services publics est modifiée conformément aux dispositions qui figurent en annexe.</p>
    </div><a style="text-decoration: none;" id="JORFARTI000036150831" name="JORFARTI000036150831"> </a><div class="article">
    <div class="titreArt">Article 2</div>
    <p>
    <br>Le directeur général de la santé et la directrice de la sécurité sociale sont chargés, chacun en ce qui le concerne, de l'exécution du présent arrêté, qui sera publié ainsi que son annexe au Journal officiel de la République française.</p>
    </div><ul>
    <li>
    <div style="margin-top: 30px; margin-bottom:20px;" id="JORFSCTA000036150832" class="titreSection">Annexe </div>
    <a style="text-decoration: none;" id="JORFARTI000036150833" name="JORFARTI000036150833"> </a>
    <div class="article">
    <p>
    <br>ANNEXE<br>(1 inscription)</p>
    <p>
    <br>La spécialité pharmaceutique suivante est inscrite sur la liste des médicaments agréés à l'usage des collectivités et divers services publics.<br>Les indications thérapeutiques ouvrant droit à la prise en charge par l'assurance maladie sont, pour la spécialité visée ci-dessous :</p>
    <p>
    <br>- en monothérapie dans le traitement des patients adultes atteints d'un mélanome avancé (non résécable ou métastatique) ;<br>- traitement des patients adultes atteints d'un cancer bronchique non à petites cellules (CBNPC) localement avancé ou métastatique dont les tumeurs expriment PD-L1, et ayant reçu au moins une chimiothérapie antérieure, les patients présentant des mutations tumorales d'EGFR ou d'ALK ayant préalablement reçu un traitement autorisé pour ces mutations ;<br>- en monothérapie dans le traitement de première ligne des patients adultes atteints d'un cancer bronchique non à petites cellules (CBNPC) métastatique dont les tumeurs expriment PD-L1 avec un score de proportion tumorale (TPS) ≥ 50 %, sans mutations tumorales d'EGFR ou d'ALK.</p>
    <p>
    </p><div align="center">
    <center>
    <table border="1">
    <tbody><tr>
    <th>
    <br>Code CIP</th>
    <th>
    <br>Présentation</th>
    </tr>
    <tr>
    <td align="left">
    <br>34009 550 243 1 6</td>
    <td align="left">
    <br>KEYTRUDA 25 mg/mL (pembrolizumab), solution à diluer pour perfusion, flacon (verre) de 4 ml, boîte de 1 flacon (B/1) (laboratoires MSD FRANCE)</td>
    </tr>
    </tbody></table>
    </center>
    </div>
    <p></p>
    <p>
    <br>(1 extension d'indication)</p>
    <p>
    <br>La prise en charge de la spécialité ci-dessous est étendue à l'indication suivante :</p>
    <p>
    <br>- en monothérapie dans le traitement de première ligne des patients adultes atteints d'un cancer bronchique non à petites cellules (CBNPC) métastatique dont les tumeurs expriment PD-L1 avec un score de proportion tumorale (TPS) ≥ 50 %, sans mutations tumorales d'EGFR ou d'ALK.</p>
    <p>
    </p><div align="center">
    <center>
    <table border="1">
    <tbody><tr>
    <th>
    <br>Code CIP</th>
    <th>
    <br>Présentation</th>
    </tr>
    <tr>
    <td align="left">
    <br>34009 550 065 5 8</td>
    <td align="left">
    <br>KEYTRUDA 50 mg (pembrolizumab) poudre pour solution à diluer pour perfusion en flacon (verre) de 15 ml (laboratoires MSD FRANCE)</td>
    </tr>
    </tbody></table>
    </center>
    </div>
    <p></p>
    </div>
    </li>
    </ul>
    </div><!-- end texte -->
    <div>
    <p align="left">
    <br>Fait le 24 novembre 2017.<br>
    </p>
    <p align="left">
    <br>La ministre des solidarités et de la santé,<br>
    <br>Pour la ministre et par délégation :<br>
    <br>La sous-directrice de la politique des produits de santé et de la qualité des pratiques et des soins,<br>
    <br>C. Perruchon<br>
    <br>Le sous-directeur du financement du système de soins,<br>
    <br>T. Wanecq<br>
    </p>
    <p align="left">
    <br>Le ministre de l'action et des comptes publics,<br>
    <br>Pour le ministre et par délégation :<br>
    <br>Le sous-directeur du financement du système de soins,<br>
    <br>T. Wanecq<br>
    </p>
    </div><!-- end signataires -->
    <!-- end nota -->
    </div><!-- end contenu -->
    <hr>
    <div id="exportRTF">
    <span class="exportRTF" about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/rtf" rel="eli:embodies" resource="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr" typeof="eli:Format"></span>
    <span about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/rtf" rel="eli:format" resource="http://www.iana.org/assignments/media-types/application/rtf"></span>
    <span class="exportRTF" about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr" rel="eli:is_embodied_by" resource="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/rtf" typeof="eli:LegalExpression"></span>
    <span class="exportRTF">
    <a href="/telecharger_rtf.do?idTexte=JORFTEXT000036150826&amp;dateTexte=29990101" title="Télécharger le document en RTF (poids < 1Mo) - Arrêté du 24 novembre 2017" onclick=" return xt_click(this,'C','1','Telechargements::RTF::Arrete_du_24_novembre_2017','T') ">
    Télécharger le document en RTF (poids &lt; 1Mo)
    </a>
    <span class="publisher" about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/rtf" property="eli:publisher" content="DILA (Direction de l'information légale et administrative)"></span>
    </span>
    <span class="fac_simile" about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/pdf" rel="eli:embodies" resource="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr" typeof="eli:Format">
    <span about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/pdf" rel="eli:format" resource="http://www.iana.org/assignments/media-types/application/pdf"></span>
    <span class="fac_simile" about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr" rel="eli:is_embodied_by" resource="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/pdf" typeof="eli:LegalExpression"></span>
    <a onclick="return xt_click(this,'C','1','Telechargements::Fac_simile::Arrete_du_24_novembre_2017','T')" title="Extrait du Journal officiel électronique authentifié (format: pdf, poids : 0.18 Mo) (Nouvelle fenêtre)" href="/jo_pdf.do?id=JORFTEXT000036150826">
    Extrait du Journal officiel électronique authentifié (format: pdf, poids : 0.18 Mo)
    </a>
    <span class="publisher" about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/pdf" property="eli:publisher" content="DILA (Direction de l'information légale et administrative)"></span>
    <span about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/pdf" property="eli:legal_value" content="definitive"></span>
    </span>
    <span class="fac_simile">
    <span class="exportRDF" about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/rdf" rel="eli:embodies" resource="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr" typeof="eli:Format"></span>
    <span about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/rdf" rel="eli:format" resource="http://www.iana.org/assignments/media-types/application/rdf"></span>
    <span class="exportRDF" about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr" rel="eli:is_embodied_by" resource="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/rdf" typeof="eli:LegalExpression"></span>
    <a href="/jo_rdf.do?cidTexte=JORFTEXT000036150826" title="Télécharger le document en RDF (format: rdf, poids < 1 Mo) - Arrêté du 24 novembre 2017 (Nouvelle fenêtre)" onclick="return xt_click(this,'C','1','Telechargements::RDF::Arrete_du_24_novembre_2017','T')">
    Télécharger le document en RDF (format: rdf, poids &lt; 1 Mo)
    </a>
    <span class="publisher" about="https://www.legifrance.gouv.fr/eli/arrete/2017/11/24/SSAS1731442A/jo/texte/fr/rdf" property="eli:publisher" content="DILA (Direction de l'information légale et administrative)"></span>
    </span>
    <br><br>
    </div><!-- end export rtf -->
    </div>
    </div>
"""

soup = BeautifulSoup(testDocument, 'html.parser')
newSoup = parseTables(soup)

print(newSoup)
print(parsedTables)
