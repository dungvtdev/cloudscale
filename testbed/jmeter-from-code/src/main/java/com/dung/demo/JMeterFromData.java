package com.dung.demo;

import org.apache.jmeter.config.Arguments;
import org.apache.jmeter.config.gui.ArgumentsPanel;
import org.apache.jmeter.control.LoopController;
import org.apache.jmeter.control.gui.LoopControlPanel;
import org.apache.jmeter.control.gui.TestPlanGui;
import org.apache.jmeter.engine.StandardJMeterEngine;
import org.apache.jmeter.gui.util.PowerTableModel;
import org.apache.jmeter.protocol.http.control.gui.HttpTestSampleGui;
import org.apache.jmeter.protocol.http.sampler.HTTPSamplerProxy;
import org.apache.jmeter.reporters.ResultCollector;
import org.apache.jmeter.reporters.Summariser;
import org.apache.jmeter.save.SaveService;
import org.apache.jmeter.testelement.TestElement;
import org.apache.jmeter.testelement.TestPlan;
import org.apache.jmeter.testelement.property.CollectionProperty;
import org.apache.jmeter.threads.ThreadGroup;
import org.apache.jmeter.threads.gui.ThreadGroupGui;
import org.apache.jmeter.util.JMeterUtils;
import org.apache.jorphan.collections.HashTree;

import java.io.File;
import java.io.FileOutputStream;

import kg.apc.jmeter.threads.UltimateThreadGroup;
import kg.apc.jmeter.threads.UltimateThreadGroupGui;
import kg.apc.jmeter.JMeterPluginsUtils;
import com.dung.demo.DataList;


public class JMeterFromData {
    public static int WSIZE = 60;
    public static int MAXTHREAD = 35;

    public static PowerTableModel getTable(String file, int begin, int end) {
        DataList dl = new DataList(file, begin, end);
        double[] data = dl.getData();
//        double[] values = new double[data.length];
//        for (int i = 0; i < data.length; i++) {
//            values[i] = (int) (data[i] * MAXTHREAD);
//            if (values[i] <= 0) values[i] = 2;
//        }
        PowerTableModel dataModel = new PowerTableModel(UltimateThreadGroupGui.columnIdentifiers, UltimateThreadGroupGui.columnClasses);
        int start = 0;
        for (int i = 0; i < data.length; i++) {
            int val = (int) (data[i] * MAXTHREAD);
            if(val > 0)
                dataModel.addRow(new Integer[]{val, start, 0, WSIZE, 0});
            start += WSIZE;
        }
        return dataModel;
    }

    public static void main(String[] argv) throws Exception {

        File jmeterHome = new File(System.getProperty("jmeter.home"));
        String slash = System.getProperty("file.separator");

        if (jmeterHome.exists()) {
            File jmeterProperties = new File(jmeterHome.getPath() + slash + "bin" + slash + "jmeter.properties");
            if (jmeterProperties.exists()) {
                //JMeter Engine
                StandardJMeterEngine jmeter = new StandardJMeterEngine();

                //JMeter initialization (properties, log levels, locale, etc)
                JMeterUtils.setJMeterHome(jmeterHome.getPath());
                JMeterUtils.loadJMeterProperties(jmeterProperties.getPath());
                JMeterUtils.initLogging();// you can comment this line out to see extra log messages of i.e. DEBUG level
                JMeterUtils.initLocale();

                // JMeter Test Plan, basically JOrphan HashTree
                HashTree testPlanTree = new HashTree();

                String file = System.getProperty("cf.file", "/home/dungvt/SpaceYZ/projects/graduation/10min_workload.csv");
                int begin = Integer.parseInt(System.getProperty("cf.begin", String.valueOf(48 * 142)));
                int end = Integer.parseInt(System.getProperty("cf.end", String.valueOf(55 * 142)));
                PowerTableModel dataModel = getTable(file, begin, end);

                // Ultimate Thread Group
                UltimateThreadGroup threadGroup = new UltimateThreadGroup();
                threadGroup.setName("Test thread group");
                CollectionProperty prop = JMeterPluginsUtils.tableModelRowsToCollectionProperty(dataModel, UltimateThreadGroup.DATA_PROPERTY);
                threadGroup.setData(prop);
                threadGroup.setProperty(TestElement.TEST_CLASS, UltimateThreadGroup.class.getName());
                threadGroup.setProperty(TestElement.GUI_CLASS, UltimateThreadGroupGui.class.getName());

                // Thread Group
//                ThreadGroup threadGroup = new ThreadGroup();
//                threadGroup.setName("Example Thread Group");
//                threadGroup.setNumThreads(1);
//                threadGroup.setRampUp(1);
//                threadGroup.setSamplerController(loopController);
//                threadGroup.setProperty(TestElement.TEST_CLASS, ThreadGroup.class.getName());
//                threadGroup.setProperty(TestElement.GUI_CLASS, ThreadGroupGui.class.getName());

                // Second HTTP Sampler - open blazemeter.com
                HTTPSamplerProxy blazemetercomSampler = new HTTPSamplerProxy();
                blazemetercomSampler.setDomain("blazemeter.com");
                blazemetercomSampler.setPort(80);
                blazemetercomSampler.setPath("/");
                blazemetercomSampler.setMethod("GET");
                blazemetercomSampler.setName("Open blazemeter.com");
                blazemetercomSampler.setProperty(TestElement.TEST_CLASS, HTTPSamplerProxy.class.getName());
                blazemetercomSampler.setProperty(TestElement.GUI_CLASS, HttpTestSampleGui.class.getName());

                // Test Plan
                TestPlan testPlan = new TestPlan("Create JMeter Script From Java Code");
                testPlan.setProperty(TestElement.TEST_CLASS, TestPlan.class.getName());
                testPlan.setProperty(TestElement.GUI_CLASS, TestPlanGui.class.getName());
                testPlan.setUserDefinedVariables((Arguments) new ArgumentsPanel().createTestElement());

                // Construct Test Plan from previously initialized elements
                testPlanTree.add(testPlan);
                HashTree threadGroupHashTree = testPlanTree.add(testPlan, threadGroup);
                threadGroupHashTree.add(blazemetercomSampler);

                // save generated test plan to JMeter's .jmx file format
                SaveService.saveTree(testPlanTree, new FileOutputStream(jmeterHome + slash + "test1.jmx"));

//                //add Summarizer output to get test progress in stdout like:
//                // summary =      2 in   1.3s =    1.5/s Avg:   631 Min:   290 Max:   973 Err:     0 (0.00%)
//                Summariser summer = null;
//                String summariserName = JMeterUtils.getPropDefault("summariser.name", "summary");
//                if (summariserName.length() > 0) {
//                    summer = new Summariser(summariserName);
//                }
//
//
//                // Store execution results into a .jtl file
//                String logFile = jmeterHome + slash + "example.jtl";
//                ResultCollector logger = new ResultCollector(summer);
//                logger.setFilename(logFile);
//                testPlanTree.add(testPlanTree.getArray()[0], logger);
//
//                // Run Test Plan
//                jmeter.configure(testPlanTree);
//                jmeter.run();

//                System.out.println("Test completed. See " + jmeterHome + slash + "test1.jtl file for results");
                System.out.println("JMeter .jmx script is available at " + jmeterHome + slash + "test1.jmx");
                System.exit(0);

            }
        }

        System.err.println("jmeter.home property is not set or pointing to incorrect location");
        System.exit(1);


    }
}
