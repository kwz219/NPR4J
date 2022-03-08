MONGO_URL="mongodb://localhost:27017/"
DATABASE="BF_Methods"
COMMIT_COL="commit"
METHOD_COL="Minfo"
BUG_COL="Buginfo"
Defects4j_repos=["jfreechart","commons-cli","closure-compiler","commons-codec","commons-collections","commons-compress","commons-csv","gson",
                 "jackson-core","jackson-databind","jackson-dataformat-xml","jsoup","commons-jxpath","commons-lang","commons-math","mockito","joda-time"]
"""
Bears_repos=['2018swecapstone/h2ms', 'Activiti/Activiti', 'Activiti/activiti-cloud-app-service', 'aicis/fresco', 'albfernandez/GDS-PMD-Security-Rules', 'apache/incubator-dubbo', 'apache/incubator-servicecomb-java-chassis', 'apache/incubator-tamaya', 'apache/jackrabbit-oak', 'apereo/java-cas-client', 'aws/aws-encryption-sdk-java', 'awslabs/amazon-kinesis-client', 'AxonFramework/AxonFramework', 'Blazebit/blaze-persistence', 'brettwooldridge/HikariCP', 'classgraph/classgraph', 'CorfuDB/CorfuDB', 'cpesch/RouteConverter', 'CSU-CS414-WareWolves/cs414-f18-001-WareWolves', 'ctripcorp/apollo', 'danfickle/openhtmltopdf', 'DataBiosphere/consent-ontology', 'debezium/debezium', 'dhis2/dhis2-core', 'DmitriiSerikov/money-transfer-service', 'dungba88/libra', 'EnMasseProject/enmasse',
             'FasterXML/jackson-databind', 'FasterXML/jackson-dataformats-binary', 'FasterXML/jackson-dataformats-text', 'hexagonframework/spring-data-ebean',
             'HubSpot/Baragon', 'INRIA/spoon', 'javadev/underscore-java', 'jenkinsci/ansicolor-plugin', 'jgrapht/jgrapht', 'julianps/modelmapper-module-vavr',
             'kmehrunes/valuestreams', 'lettuce-io/lettuce-core', 'linkedin/pinot', 'milaboratory/milib', 'molgenis/molgenis', 'OpenFeign/feign',
             'openmrs/openmrs-module-htmlformentry', 'openmrs/openmrs-module-webservices.rest', 'opentracing-contrib/java-p6spy', 'openzipkin/zipkin',
             'org-tigris-jsapar/jsapar', 'paritytrading/foundation', 'pippo-java/pippo', 'rafonsecad/cash-count', 'raphw/byte-buddy', 'rkonovalov/jsonignore',
             'shapesecurity/shift-java', 'smallcreep/cucumber-seeds', 'societe-generale/ci-droid-tasks-consumer', 'SonarOpenCommunity/sonar-cxx',
             'SpoonLabs/gumtree-spoon-ast-diff', 'spring-cloud/spring-cloud-gcp', 'spring-projects/spring-data-commons', 'spring-projects/spring-data-jpa',
             'square/javapoet', 'swagger-api/swagger-codegen', 'SzFMV2018-Tavasz/AutomatedCar', 'thelastpickle/cassandra-reaper', 'thelinmichael/spotify-web-api-java',
             'traccar/traccar', 'vert-x3/vertx-jdbc-client', 'vert-x3/vertx-web', 'vitorenesduarte/VCD-java-client', 'vkostyukov/la4j', 'webfirmframework/wff']
"""
Bears_repos=['h2ms', 'Activiti', 'activiti-cloud-app-service', 'fresco', 'GDS-PMD-Security-Rules', 'incubator-dubbo', 'incubator-servicecomb-java-chassis', 'incubator-tamaya', 'jackrabbit-oak', 'java-cas-client', 'aws-encryption-sdk-java', 'amazon-kinesis-client', 'AxonFramework', 'blaze-persistence', 'HikariCP', 'classgraph', 'CorfuDB', 'RouteConverter', 'cs414-f18-001-WareWolves', 'apollo', 'openhtmltopdf', 'consent-ontology', 'debezium', 'dhis2-core', 'money-transfer-service', 'libra', 'enmasse',
             'jackson-databind', 'jackson-dataformats-binary', 'jackson-dataformats-text', 'spring-data-ebean',
             'Baragon', 'spoon', 'underscore-java', 'ansicolor-plugin', 'jgrapht', 'modelmapper-module-vavr',
             'valuestreams', 'lettuce-core', 'pinot', 'milib', 'molgenis', 'feign',
             'openmrs-module-htmlformentry', 'openmrs-module-webservices.rest', 'java-p6spy', 'zipkin',
             'jsapar', 'foundation', 'pippo', 'cash-count', 'byte-buddy', 'jsonignore',
             'shift-java', 'cucumber-seeds', 'ci-droid-tasks-consumer', 'sonar-cxx',
             'gumtree-spoon-ast-diff', 'spring-cloud-gcp', 'spring-data-commons', 'spring-data-jpa',
             'javapoet', 'swagger-codegen', 'AutomatedCar', 'cassandra-reaper', 'spotify-web-api-java',
             'traccar', 'vertx-jdbc-client', 'vertx-web', 'VCD-java-client', 'la4j', 'wff']
Bugs_dot_jar_repos=['accumulo','camel','commons-math','flink','jackrabbit-oak','logging-log4j2','maven','wicket']
Benchmark_repos=['defects4j','IntroClassJava','QuixBugs','bugs-dot-jar','bears-benchmark']
APR_tool_repos=['nopol','DiffTGen','ssFix','ACS','genesis-rep','npefix','bugfixes','astor','arja']

SEP='<sep>'