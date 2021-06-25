<?xml version="1.0" encoding="UTF-8"?>
<tileset name="base" tilewidth="32" tileheight="32" spacing="1" tilecount="9" columns="3">
 <image source="numbers.png" width="100" height="100"/>
 <tile id="0">
  <properties>
   <property name="number" type="int" value="1"/>
  </properties>
  <objectgroup draworder="index">
   <object id="0" x="11.75" y="4.75" width="10.25" height="25.25"/>
  </objectgroup>
 </tile>
 <tile id="1">
  <properties>
   <property name="number" type="int" value="2"/>
  </properties>
 </tile>
 <tile id="2">
  <properties>
   <property name="number" type="int" value="3"/>
  </properties>
 </tile>
 <tile id="4" type="five"/>
 <tile id="6">
  <animation>
   <frame tileid="0" duration="200"/>
   <frame tileid="1" duration="300"/>
   <frame tileid="2" duration="400"/>
   <frame tileid="3" duration="500"/>
   <frame tileid="4" duration="600"/>
   <frame tileid="5" duration="700"/>
   <frame tileid="6" duration="2000"/>
  </animation>
 </tile>
</tileset>
