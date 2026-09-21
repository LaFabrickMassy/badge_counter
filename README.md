# Compteur de fréquentation

## Objectif

Ce projet décrit un appareil qui permet de mesurer la fréquentation d'un lieu.  
Il a pour prérequis que tous les visiteurs disposeraient d'un badge à technologie NFC (typiquement salariés d'une entreprise), et badgent volontairement (présence nécessaire d'un panneau d'invitation au badgeage).

## Principe
Les badgeages sont enregistrés, et les statistiques sont accessible sur un serveur web local (hotspot) sous forme de statistiques par période de temps (nombre de visites mensuelles, nombre de visiteurs uniques mensuels).  
L'appareil est complètement autonome et n'est relié a rien si ce n'est son alimentation électrique.  
L'appareil n'enregistre que des identifiants de badge (nécessaire pour déterminer les visiteurs uniques), et n'a pas accès aux données personnelles (nom du porteur du badge par exemple).  


## Fonctionnement 
Au badgeage, un musique aléatoire (parmi 4 pour l’instant) est jouée.  
Il y a un « anti-passback », qui inhibe le badgeage pendant 1h pour chaque badge.  
Discriminant de badge : identifiant à n chiffres sur un bloc de m octets (cas des badges des salariés du site du FabLab).  

## Restitution des données

Un hotspot wifi et un serveur web sont démarrés lorsqu’on appuie sur le bouton de coté (et s’arrêtent au bout de 10 minutes). Les credentials (SSID, pwd, ip) sont affichés sur l’écran lorsque le serveur est actif.
Le serveur web donne accès aux données de fréquentation mensuelles sous forme tabulaire et graphique.
Il y a une page d’administration qui permet de  
- regler l’heure et de
- télécharger un fichier de synthèse des statistiques,
- téléchargerle fichier de log (timestamp, id badge)
- mais aussi d’écraser le fichier de log (attention, remise à zero des stats). Par sécurité, un backup est fait sur la carte, accessible uniquement physiquement (par lecture de la carte sd sur un pc).
