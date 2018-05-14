Title: 配置 Maven 自动化构建 protobuf 代码依赖
Date: 2018-05-14
Author: xiayf
Slug: maven-protobuf
Tags: java, maven, protobuf


1.pom.xml 中添加如下属性配置：

```xml
<properties>
    <!-- protobuf paths -->
    <protobuf.input.directory>${project.basedir}/src/main/protobuf</protobuf.input.directory>
    <protobuf.output.directory>${project.build.directory}/generated-sources</protobuf.output.directory>
    <!-- library versions -->
    <build-helper-maven-plugin.version>3.0.0</build-helper-maven-plugin.version>
    <maven-antrun-plugin.version>1.8</maven-antrun-plugin.version>
    <maven-dependency-plugin.version>3.0.2</maven-dependency-plugin.version>
    <os-maven-plugin.version>1.5.0.Final</os-maven-plugin.version>
    <protobuf.version>2.5.0</protobuf.version>
</properties>
```

2.添加 protobuf-java 库依赖

```xml
<dependencies>
    <dependency>
        <groupId>com.google.protobuf</groupId>
        <artifactId>protobuf-java</artifactId>
        <version>${protobuf.version}</version>
    </dependency>
</dependencies>
```

3.添加 maven 扩展：

```xml
<build>
    <extensions>
        <!-- provides os.detected.classifier (i.e. linux-x86_64, osx-x86_64) property -->
        <extension>
            <groupId>kr.motd.maven</groupId>
            <artifactId>os-maven-plugin</artifactId>
            <version>${os-maven-plugin.version}</version>
        </extension>
    </extensions>
</build>
```

4.配置构建插件：

```xml
<build>
    <plugins>
        <!-- copy protoc binary into build directory -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-dependency-plugin</artifactId>
            <version>${maven-dependency-plugin.version}</version>
            <executions>
                <execution>
                    <id>copy-protoc</id>
                    <phase>generate-sources</phase>
                    <goals>
                        <goal>copy</goal>
                    </goals>
                    <configuration>
                        <artifactItems>
                            <artifactItem>
                                <groupId>com.google.protobuf</groupId>
                                <artifactId>protoc</artifactId>
                                <version>${protobuf.version}</version>
                                <classifier>${os.detected.classifier}</classifier>
                                <type>exe</type>
                                <overWrite>true</overWrite>
                                <outputDirectory>${project.build.directory}</outputDirectory>
                            </artifactItem>
                        </artifactItems>
                    </configuration>
                </execution>
            </executions>
        </plugin>
        <!-- compile proto buffer files using copied protoc binary -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-antrun-plugin</artifactId>
            <version>${maven-antrun-plugin.version}</version>
            <executions>
                <execution>
                    <id>exec-protoc</id>
                    <phase>generate-sources</phase>
                    <configuration>
                        <target>
                            <property name="protoc.filename" value="protoc-${protobuf.version}-${os.detected.classifier}.exe"/>
                            <property name="protoc.filepath" value="${project.build.directory}/${protoc.filename}"/>
                            <chmod file="${protoc.filepath}" perm="ugo+rx"/>
                            <mkdir dir="${protobuf.output.directory}" />
                            <path id="protobuf.input.filepaths.path">
                                <fileset dir="${protobuf.input.directory}">
                                    <include name="**/*.proto"/>
                                </fileset>
                            </path>
                            <pathconvert pathsep=" " property="protobuf.input.filepaths" refid="protobuf.input.filepaths.path"/>
                            <exec executable="${protoc.filepath}" failonerror="true">
                                <arg value="-I"/>
                                <arg value="${protobuf.input.directory}"/>
                                <arg value="--java_out"/>
                                <arg value="${protobuf.output.directory}"/>
                                <arg line="${protobuf.input.filepaths}"/>
                            </exec>
                        </target>
                    </configuration>
                    <goals>
                        <goal>run</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
        <!-- add generated proto buffer classes into the package -->
        <plugin>
            <groupId>org.codehaus.mojo</groupId>
            <artifactId>build-helper-maven-plugin</artifactId>
            <version>${build-helper-maven-plugin.version}</version>
            <executions>
                <execution>
                    <id>add-classes</id>
                    <phase>generate-sources</phase>
                    <goals>
                        <goal>add-source</goal>
                    </goals>
                    <configuration>
                        <sources>
                            <source>${protobuf.output.directory}</source>
                        </sources>
                    </configuration>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

**参考资料**

http://vlkan.com/blog/post/2015/11/27/maven-protobuf/

http://www.chendan.me/2017/07/02/maven-protobuf/



