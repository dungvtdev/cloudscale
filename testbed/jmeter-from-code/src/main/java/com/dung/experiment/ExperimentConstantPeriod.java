package com.dung.experiment;

import org.apache.jmeter.config.Arguments;
import org.apache.jmeter.config.gui.ArgumentsPanel;
import org.apache.jmeter.control.gui.TestPlanGui;
import org.apache.jmeter.engine.StandardJMeterEngine;
import org.apache.jmeter.gui.util.PowerTableModel;
import org.apache.jmeter.save.SaveService;
import org.apache.jmeter.testelement.TestElement;
import org.apache.jmeter.testelement.TestPlan;
import org.apache.jmeter.testelement.property.CollectionProperty;
import org.apache.jmeter.util.JMeterUtils;
import org.apache.jorphan.collections.HashTree;

import java.io.File;
import java.io.FileOutputStream;

import kg.apc.jmeter.threads.UltimateThreadGroup;
import kg.apc.jmeter.threads.UltimateThreadGroupGui;
import kg.apc.jmeter.JMeterPluginsUtils;

public class ExperimentConstantPeriod {
    /**
     * @param maxThread:    so thread toi da (chua tinh random)
     * @param randomRatio:  [0,1] random so thread o moi chu ky
     * @param periodTime:   thoi gian tinh theo minute moi chu ky
     * @param periodNumber: so chu ky muon tao
     */
    static PowerTableModel getRandomModel(int maxThread, float randomRatio, int periodTime, int periodNumber) {
        int[][] data = new int[][]{
                {10, 0, 120, 500, 200},
                {22, 85, 100, 20, 150},
                {25, 380, 70, 60, 100},
                {15, 280, 80, 10, 30}
        };

        int originMaxThread = 34;
        int originPeriod = 720;
        float localRandomRatio = 0.15f;


        if (maxThread == 0) maxThread = originMaxThread;
        if (periodTime == 0) periodTime = originPeriod;

        PowerTableModel dataModel = new PowerTableModel(UltimateThreadGroupGui.columnIdentifiers, UltimateThreadGroupGui.columnClasses);

        // fix data

        float yRatio = maxThread * 1.0f / originMaxThread;
        float xRatio = periodTime * 1.0f / originPeriod;

        for (int r = 0; r < data.length; r++) {
            int[] row = data[r];
            row[0] = (int) (row[0] * yRatio);
            for (int c = 1; c < row.length; c++) {
                row[c] = (int) (row[c] * xRatio);
            }
        }

        // create data with random
        for (int p = 0; p < periodNumber; p++) {
            int begin = p * periodTime;

            double ratio = (Math.random() * 2 - 1) * randomRatio;
            ratio = 1 + ratio;

            for (int r = 0; r < data.length; r++) {
                int[] row = data[r];
                double localRatio = (Math.random() * 2 - 1) * localRandomRatio + 1;

                dataModel.addRow(new Integer[]{
                        (int) (row[0] * ratio * localRatio),
                        (begin + row[1]) * 60,
                        row[2] * 60,
                        row[3] * 60,
                        row[4] * 60,
                });
            }
        }

        return dataModel;
    }

    public static void main(String[] argv) throws Exception {

        File jmeterHome = new File(System.getProperty("jmeter.home"));
        String slash = System.getProperty("file.separator");

        if (jmeterHome.exists()) {
            File jmeterProperties = new File(jmeterHome.getPath() + slash + "bin" + slash + "jmeter.properties");
            if (jmeterProperties.exists()) {

                //JMeter initialization (properties, log levels, locale, etc)
                JMeterUtils.setJMeterHome(jmeterHome.getPath());
                JMeterUtils.loadJMeterProperties(jmeterProperties.getPath());
                JMeterUtils.initLogging();// you can comment this line out to see extra log messages of i.e. DEBUG level
                JMeterUtils.initLocale();

                // JMeter Test Plan, basically JOrphan HashTree
                HashTree testPlanTree = new HashTree();

                int maxThread = Integer.parseInt(System.getProperty("cf.thread", "0"));
                int periodTime = Integer.parseInt(System.getProperty("cf.period", "0"));
                int periodNumber = Integer.parseInt(System.getProperty("cf.nPeriod", "0"));
                float randomRatio = Float.parseFloat(System.getProperty("cf.rand", "0"));

                PowerTableModel dataModel = getRandomModel(maxThread, randomRatio, periodTime, periodNumber);

                // Ultimate Thread Group
                UltimateThreadGroup threadGroup = new UltimateThreadGroup();
                threadGroup.setName("Test thread group");
                CollectionProperty prop = JMeterPluginsUtils.tableModelRowsToCollectionProperty(dataModel, UltimateThreadGroup.DATA_PROPERTY);
                threadGroup.setData(prop);
                threadGroup.setProperty(TestElement.TEST_CLASS, UltimateThreadGroup.class.getName());
                threadGroup.setProperty(TestElement.GUI_CLASS, UltimateThreadGroupGui.class.getName());


                // Test Plan
                TestPlan testPlan = new TestPlan("Create JMeter Script From Java Code");
                testPlan.setProperty(TestElement.TEST_CLASS, TestPlan.class.getName());
                testPlan.setProperty(TestElement.GUI_CLASS, TestPlanGui.class.getName());
                testPlan.setUserDefinedVariables((Arguments) new ArgumentsPanel().createTestElement());

                // Construct Test Plan from previously initialized elements
                testPlanTree.add(testPlan);
                HashTree threadGroupHashTree = testPlanTree.add(testPlan, threadGroup);


                // save generated test plan to JMeter's .jmx file format
                String fileOutput = System.getProperty("cf.file", "");
                SaveService.saveTree(testPlanTree, new FileOutputStream(fileOutput));


                System.out.println("JMeter .jmx script is available at " + fileOutput);
                System.exit(0);

            }
        }

        System.err.println("jmeter.home property is not set or pointing to incorrect location");
        System.exit(1);

    }
}
