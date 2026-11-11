/*
 * MANET AAT: AODV vs DSDV performance comparison.
 *
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * The ad-hoc 802.11b / Friis / Random Waypoint setup follows the installed
 * NS-3.45 example examples/routing/manet-routing-compare.cc
 * (Justin Rohrer, University of Kansas, GPL-2.0-only). This file is a new
 * scratch program: it does not modify that example.
 *
 * Application metrics use only the three configured UDP flows
 * (destination ports 9000, 9001 and 9002).
 */

#include "ns3/aodv-module.h"
#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/dsdv-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/netanim-module.h"
#include "ns3/network-module.h"
#include "ns3/yans-wifi-helper.h"

#include <chrono>
#include <cmath>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

using namespace ns3;

namespace
{

constexpr uint16_t kUdpProtocol = 17;
constexpr uint16_t kPorts[3] = {9000, 9001, 9002};
constexpr double kAppStartS = 5.0;
constexpr double kAppStopS = 60.0;
constexpr double kSimStopS = 65.0;
constexpr double kMeasurementS = kAppStopS - kAppStartS; // 55 s
constexpr uint32_t kPacketSize = 512;
constexpr char kDataRate[] = "64kb/s"; // ns-3 DataRate: 1 kb/s = 1000 bit/s
constexpr char kPhyMode[] = "DsssRate11Mbps";
constexpr char kWifiStandard[] = "802.11b";
constexpr char kPropagation[] = "FriisPropagationLossModel";
// version.h is installed only when ./ns3 configure --enable-build-version is used.
constexpr char kNs3Version[] = "3.45";
constexpr char kBuildProfile[] = "optimized";

struct Options
{
    std::string protocol;
    uint32_t numNodes = 10;
    double nodeSpeed = 10.0;
    double nodePause = 0.0;
    uint32_t seed = 12345;
    uint32_t run = 1;
    std::string outputDir;
    uint32_t enableAnimation = 0;
    uint32_t overwrite = 0;
    double areaX = 500.0;
    double areaY = 500.0;
    double txPowerDbm = 7.5;
};

struct FlowTotals
{
    uint64_t txPackets = 0;
    uint64_t rxPackets = 0;
    uint64_t txBytes = 0;
    uint64_t rxBytes = 0;
    double delaySumS = 0.0;
    uint64_t lostPackets = 0;
    double jitterSumS = 0.0;
    uint32_t selectedFlows = 0;
    uint32_t flowsWithTx = 0;
};

void
Fail(const std::string& message)
{
    std::cerr << "manet-aat: error: " << message << "\n";
    std::exit(1);
}

std::string
Upper(std::string value)
{
    for (char& ch : value)
    {
        if (ch >= 'a' && ch <= 'z')
        {
            ch = static_cast<char>(ch - 'a' + 'A');
        }
    }
    return value;
}

std::string
JsonEscape(const std::string& input)
{
    std::string out;
    for (char ch : input)
    {
        switch (ch)
        {
        case '\\':
            out += "\\\\";
            break;
        case '"':
            out += "\\\"";
            break;
        case '\n':
            out += "\\n";
            break;
        default:
            out.push_back(ch);
        }
    }
    return out;
}

std::string
CsvQuote(const std::string& input)
{
    std::string out = "\"";
    for (char ch : input)
    {
        if (ch == '"')
        {
            out += "\"\"";
        }
        else
        {
            out.push_back(ch);
        }
    }
    out.push_back('"');
    return out;
}

std::string
UtcNow()
{
    const std::time_t now = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
    std::tm parts{};
    gmtime_r(&now, &parts);
    std::ostringstream os;
    os << std::put_time(&parts, "%Y-%m-%dT%H:%M:%SZ");
    return os.str();
}

std::string
JoinArgs(int argc, char** argv)
{
    std::ostringstream os;
    for (int i = 0; i < argc; ++i)
    {
        if (i)
        {
            os << ' ';
        }
        os << argv[i];
    }
    return os.str();
}

bool
Near(double value, double target)
{
    return std::fabs(value - target) < 1e-9;
}

Options
ParseOptions(int argc, char** argv)
{
    Options opt;
    std::string protocol = "AODV";
    CommandLine cmd(__FILE__);
    cmd.AddValue("protocol", "Routing protocol: AODV or DSDV", protocol);
    cmd.AddValue("numNodes", "Number of ad-hoc nodes (10 or 20)", opt.numNodes);
    cmd.AddValue("nodeSpeed", "Random Waypoint speed in m/s (5, 10 or 20)", opt.nodeSpeed);
    cmd.AddValue("nodePause", "Random Waypoint pause in seconds (must be 0)", opt.nodePause);
    cmd.AddValue("seed", "ns-3 RNG master seed", opt.seed);
    cmd.AddValue("run", "ns-3 RNG run number (1, 2 or 3)", opt.run);
    cmd.AddValue("outputDir", "Directory for this run's CSV, XML and traces", opt.outputDir);
    cmd.AddValue("enableAnimation", "Write NetAnim XML when 1", opt.enableAnimation);
    cmd.AddValue("overwrite", "Replace an existing summary.csv when 1", opt.overwrite);
    cmd.AddValue("areaX", "Playground width in meters", opt.areaX);
    cmd.AddValue("areaY", "Playground height in meters", opt.areaY);
    cmd.AddValue("txPowerDbm", "Wi-Fi transmit power in dBm", opt.txPowerDbm);
    cmd.Parse(argc, argv);

    opt.protocol = Upper(protocol);
    if (opt.protocol != "AODV" && opt.protocol != "DSDV")
    {
        Fail("protocol must be AODV or DSDV (got '" + protocol + "')");
    }
    if (opt.numNodes != 10 && opt.numNodes != 20)
    {
        Fail("numNodes must be 10 or 20");
    }
    if (!(Near(opt.nodeSpeed, 5.0) || Near(opt.nodeSpeed, 10.0) || Near(opt.nodeSpeed, 20.0)))
    {
        Fail("nodeSpeed must be 5, 10 or 20 m/s");
    }
    if (!Near(opt.nodePause, 0.0))
    {
        Fail("nodePause must be 0 seconds for this experiment");
    }
    if (opt.seed == 0)
    {
        Fail("seed must be a positive integer");
    }
    if (opt.run < 1 || opt.run > 3)
    {
        Fail("run must be 1, 2 or 3");
    }
    if (opt.outputDir.empty())
    {
        Fail("outputDir is required");
    }
    if (opt.enableAnimation > 1 || opt.overwrite > 1)
    {
        Fail("enableAnimation and overwrite must be 0 or 1");
    }
    if (!(opt.areaX > 0.0) || !(opt.areaY > 0.0))
    {
        Fail("areaX and areaY must be positive");
    }
    return opt;
}

std::string
ExperimentId(const Options& opt)
{
    std::ostringstream os;
    os << opt.protocol << "_n" << opt.numNodes << "_s" << static_cast<int>(opt.nodeSpeed)
       << "_seed" << opt.seed << "_r" << opt.run;
    return os.str();
}

void
SampleMobility(std::ofstream* out, NodeContainer nodes, uint32_t second)
{
    for (uint32_t i = 0; i < nodes.GetN(); ++i)
    {
        Ptr<MobilityModel> model = nodes.Get(i)->GetObject<MobilityModel>();
        const Vector pos = model->GetPosition();
        *out << i << "," << second << "," << pos.x << "," << pos.y << "," << pos.z << "\n";
    }
}

std::string
BlankOr(bool defined, double value)
{
    if (!defined || !std::isfinite(value))
    {
        return "";
    }
    std::ostringstream os;
    os << std::setprecision(17) << value;
    return os.str();
}

void
WriteSummary(const std::filesystem::path& path,
             const Options& opt,
             const FlowTotals& totals,
             const std::string& status,
             const std::string& warnings)
{
    const bool txOk = totals.txPackets > 0;
    const bool rxOk = totals.rxPackets > 0;
    const bool lossOk = totals.txPackets >= totals.rxPackets;
    double pdr = 0.0;
    double lossPct = 0.0;
    double delayMs = 0.0;
    double throughput = 0.0;
    if (txOk)
    {
        pdr = 100.0 * static_cast<double>(totals.rxPackets) / static_cast<double>(totals.txPackets);
        lossPct = 100.0 * static_cast<double>(totals.txPackets - totals.rxPackets) /
                  static_cast<double>(totals.txPackets);
    }
    if (rxOk)
    {
        delayMs = 1000.0 * totals.delaySumS / static_cast<double>(totals.rxPackets);
    }
    if (kMeasurementS > 0.0)
    {
        throughput = (8.0 * static_cast<double>(totals.rxBytes)) / (kMeasurementS * 1000.0);
    }

    std::ofstream out(path);
    if (!out)
    {
        Fail("cannot write " + path.string());
    }
    out << std::setprecision(17);
    out << "experiment_id,protocol,ns3_version,num_nodes,area_x_m,area_y_m,node_speed_mps,"
           "node_pause_s,seed,run,wifi_standard,phy_mode,propagation_model,tx_power_dbm,"
           "flow_count,packet_size_bytes,flow_rate_kbps,app_start_s,app_stop_s,"
           "measurement_duration_s,sim_stop_s,tx_packets,rx_packets,tx_bytes,rx_bytes,"
           "packet_loss_packets,packet_loss_percent,pdr_percent,delay_sum_s,avg_delay_ms,"
           "throughput_kbps,flowmonitor_lost_packets_diagnostic,animation_enabled,status,"
           "selected_flow_count,jitter_sum_s,warnings\n";
    out << CsvQuote(ExperimentId(opt)) << "," << CsvQuote(opt.protocol) << ","
        << CsvQuote(kNs3Version) << "," << opt.numNodes << "," << opt.areaX << ","
        << opt.areaY << "," << opt.nodeSpeed << "," << opt.nodePause << "," << opt.seed << ","
        << opt.run << "," << CsvQuote(kWifiStandard) << "," << CsvQuote(kPhyMode) << ","
        << CsvQuote(kPropagation) << "," << opt.txPowerDbm << ",3," << kPacketSize << ",64,"
        << kAppStartS << "," << kAppStopS << "," << kMeasurementS << "," << kSimStopS << ","
        << totals.txPackets << "," << totals.rxPackets << "," << totals.txBytes << ","
        << totals.rxBytes << ",";
    if (txOk && lossOk)
    {
        out << (totals.txPackets - totals.rxPackets);
    }
    out << "," << BlankOr(txOk && lossOk, lossPct) << "," << BlankOr(txOk, pdr) << ","
        << totals.delaySumS << "," << BlankOr(rxOk, delayMs) << ","
        << BlankOr(std::isfinite(throughput) && throughput >= 0.0, throughput) << ","
        << totals.lostPackets << "," << opt.enableAnimation << "," << CsvQuote(status) << ","
        << totals.selectedFlows << "," << totals.jitterSumS << "," << CsvQuote(warnings) << "\n";
}

void
WriteManifest(const std::filesystem::path& path,
              const Options& opt,
              const std::string& command,
              const std::string& started,
              const std::string& status,
              const std::string& warnings)
{
    std::ofstream out(path);
    if (!out)
    {
        Fail("cannot write " + path.string());
    }
    const std::string id = ExperimentId(opt);
    out << "{\n";
    out << "  \"project_title\": \"Performance Evaluation of AODV and DSDV Routing Protocols in "
           "Mobile Ad Hoc Networks Using NS-3\",\n";
    out << "  \"experiment_id\": \"" << JsonEscape(id) << "\",\n";
    out << "  \"ns3_version\": \"" << kNs3Version << "\",\n";
    out << "  \"ns3_build_profile\": \"" << kBuildProfile << "\",\n";
    out << "  \"command\": \"" << JsonEscape(command) << "\",\n";
    out << "  \"protocol\": \"" << opt.protocol << "\",\n";
    out << "  \"num_nodes\": " << opt.numNodes << ",\n";
    out << "  \"area_x_m\": " << opt.areaX << ",\n";
    out << "  \"area_y_m\": " << opt.areaY << ",\n";
    out << "  \"node_speed_mps\": " << opt.nodeSpeed << ",\n";
    out << "  \"node_pause_s\": " << opt.nodePause << ",\n";
    out << "  \"seed\": " << opt.seed << ",\n";
    out << "  \"run\": " << opt.run << ",\n";
    out << "  \"wifi_standard\": \"" << kWifiStandard << "\",\n";
    out << "  \"phy_mode\": \"" << kPhyMode << "\",\n";
    out << "  \"propagation_model\": \"" << kPropagation << "\",\n";
    out << "  \"tx_power_dbm\": " << opt.txPowerDbm << ",\n";
    out << "  \"flows\": [\n";
    out << "    {\"flow\": \"F1\", \"src_node\": 0, \"dst_node\": " << (opt.numNodes - 1)
        << ", \"dst_port\": 9000},\n";
    out << "    {\"flow\": \"F2\", \"src_node\": 1, \"dst_node\": " << (opt.numNodes - 2)
        << ", \"dst_port\": 9001},\n";
    out << "    {\"flow\": \"F3\", \"src_node\": 2, \"dst_node\": " << (opt.numNodes - 3)
        << ", \"dst_port\": 9002}\n";
    out << "  ],\n";
    out << "  \"packet_size_bytes\": " << kPacketSize << ",\n";
    out << "  \"flow_rate\": \"" << kDataRate << "\",\n";
    out << "  \"app_start_s\": " << kAppStartS << ",\n";
    out << "  \"app_stop_s\": " << kAppStopS << ",\n";
    out << "  \"measurement_duration_s\": " << kMeasurementS << ",\n";
    out << "  \"sim_stop_s\": " << kSimStopS << ",\n";
    out << "  \"cleanup_interval_s\": " << (kSimStopS - kAppStopS) << ",\n";
    out << "  \"animation_enabled\": " << (opt.enableAnimation ? "true" : "false") << ",\n";
    out << "  \"rng_streams\": {\n";
    out << "    \"position_allocator\": 100,\n";
    out << "    \"mobility\": 200,\n";
    out << "    \"wifi_devices\": 1000,\n";
    out << "    \"wifi_channel\": 2000,\n";
    out << "    \"aodv\": " << (opt.protocol == "AODV" ? "3000" : "null") << ",\n";
    out << "    \"dsdv_assign_streams\": \"not available on DsdvHelper in ns-3.45\"\n";
    out << "  },\n";
    out << "  \"timestamp_start_utc\": \"" << started << "\",\n";
    out << "  \"timestamp_end_utc\": \"" << UtcNow() << "\",\n";
    out << "  \"output_files\": [\"summary.csv\", \"flows.csv\", \"flowmon.xml\", "
           "\"mobility.csv\""
        << (opt.enableAnimation ? ", \"animation.xml\"" : "") << "],\n";
    out << "  \"status\": \"" << status << "\",\n";
    out << "  \"warnings\": \"" << JsonEscape(warnings) << "\",\n";
    out << "  \"exit_code\": null\n";
    out << "}\n";
}

} // namespace

int
main(int argc, char* argv[])
{
    const std::string command = JoinArgs(argc, argv);
    const std::string started = UtcNow();
    const Options opt = ParseOptions(argc, argv);

    std::filesystem::path outDir(opt.outputDir);
    std::error_code fsError;
    std::filesystem::create_directories(outDir, fsError);
    if (fsError || !std::filesystem::is_directory(outDir))
    {
        Fail("cannot create output directory '" + opt.outputDir + "'");
    }
    const std::filesystem::path summaryPath = outDir / "summary.csv";
    if (std::filesystem::exists(summaryPath) && opt.overwrite == 0)
    {
        Fail("output already exists (" + summaryPath.string() +
             "). Pass --overwrite=1 to replace it.");
    }

    RngSeedManager::SetSeed(opt.seed);
    RngSeedManager::SetRun(opt.run);

    std::cout << "=== manet-aat configuration ===\n";
    std::cout << "experiment_id: " << ExperimentId(opt) << "\n";
    std::cout << "ns3_version: " << kNs3Version << " profile=" << kBuildProfile << "\n";
    std::cout << "protocol: " << opt.protocol << "\n";
    std::cout << "num_nodes: " << opt.numNodes << "\n";
    std::cout << "area_m: " << opt.areaX << " x " << opt.areaY << "\n";
    std::cout << "node_speed_mps: " << opt.nodeSpeed << " pause_s: " << opt.nodePause << "\n";
    std::cout << "seed: " << opt.seed << " run: " << opt.run << "\n";
    std::cout << "wifi: " << kWifiStandard << " phy: " << kPhyMode
              << " propagation: " << kPropagation << " tx_power_dbm: " << opt.txPowerDbm << "\n";
    std::cout << "flows: 3 UDP  " << kDataRate << " payload " << kPacketSize
              << " bytes ports 9000,9001,9002\n";
    std::cout << "  F1 0 -> " << (opt.numNodes - 1) << " port 9000\n";
    std::cout << "  F2 1 -> " << (opt.numNodes - 2) << " port 9001\n";
    std::cout << "  F3 2 -> " << (opt.numNodes - 3) << " port 9002\n";
    std::cout << "app_window_s: " << kAppStartS << " -> " << kAppStopS
              << " measurement_s: " << kMeasurementS << " sim_stop_s: " << kSimStopS
              << " cleanup_s: " << (kSimStopS - kAppStopS) << "\n";
    std::cout << "animation: " << opt.enableAnimation << "\n";
    std::cout << "output_dir: " << outDir.string() << "\n";

    NodeContainer nodes;
    nodes.Create(opt.numNodes);

    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211b);
    wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                 "DataMode",
                                 StringValue(kPhyMode),
                                 "ControlMode",
                                 StringValue(kPhyMode));
    Config::SetDefault("ns3::WifiRemoteStationManager::NonUnicastMode", StringValue(kPhyMode));

    YansWifiChannelHelper channelHelper;
    channelHelper.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel");
    channelHelper.AddPropagationLoss("ns3::FriisPropagationLossModel");
    Ptr<YansWifiChannel> channel = channelHelper.Create();

    YansWifiPhyHelper phy;
    phy.SetChannel(channel);
    phy.Set("TxPowerStart", DoubleValue(opt.txPowerDbm));
    phy.Set("TxPowerEnd", DoubleValue(opt.txPowerDbm));

    WifiMacHelper mac;
    mac.SetType("ns3::AdhocWifiMac");
    NetDeviceContainer devices = wifi.Install(phy, mac, nodes);

    // Fixed stream indexes keep mobility independent of which routing protocol is installed.
    std::ostringstream xStream;
    xStream << "ns3::UniformRandomVariable[Min=0.0|Max=" << opt.areaX << "]";
    std::ostringstream yStream;
    yStream << "ns3::UniformRandomVariable[Min=0.0|Max=" << opt.areaY << "]";
    ObjectFactory positionFactory;
    positionFactory.SetTypeId("ns3::RandomRectanglePositionAllocator");
    positionFactory.Set("X", StringValue(xStream.str()));
    positionFactory.Set("Y", StringValue(yStream.str()));
    Ptr<PositionAllocator> positionAlloc = positionFactory.Create()->GetObject<PositionAllocator>();
    positionAlloc->AssignStreams(100);

    // Constant speed makes the nominal scenario speed the actual waypoint speed.
    std::ostringstream speedSpec;
    speedSpec << "ns3::ConstantRandomVariable[Constant=" << opt.nodeSpeed << "]";
    MobilityHelper mobility;
    mobility.SetMobilityModel("ns3::RandomWaypointMobilityModel",
                              "Speed",
                              StringValue(speedSpec.str()),
                              "Pause",
                              StringValue("ns3::ConstantRandomVariable[Constant=0.0]"),
                              "PositionAllocator",
                              PointerValue(positionAlloc));
    mobility.SetPositionAllocator(positionAlloc);
    mobility.Install(nodes);
    mobility.AssignStreams(nodes, 200);
    channelHelper.AssignStreams(channel, 2000);
    WifiHelper::AssignStreams(devices, 1000);

    InternetStackHelper internet;
    AodvHelper aodv;
    DsdvHelper dsdv;
    if (opt.protocol == "AODV")
    {
        internet.SetRoutingHelper(aodv);
    }
    else
    {
        internet.SetRoutingHelper(dsdv);
    }
    internet.Install(nodes);
    if (opt.protocol == "AODV")
    {
        aodv.AssignStreams(nodes, 3000);
    }

    Ipv4AddressHelper addresses;
    addresses.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer interfaces = addresses.Assign(devices);

    const uint32_t destinations[3] = {opt.numNodes - 1, opt.numNodes - 2, opt.numNodes - 3};
    for (uint32_t flow = 0; flow < 3; ++flow)
    {
        PacketSinkHelper sink("ns3::UdpSocketFactory",
                              InetSocketAddress(Ipv4Address::GetAny(), kPorts[flow]));
        ApplicationContainer sinkApp = sink.Install(nodes.Get(destinations[flow]));
        sinkApp.Start(Seconds(0.0));
        sinkApp.Stop(Seconds(kSimStopS));

        OnOffHelper source("ns3::UdpSocketFactory",
                           InetSocketAddress(interfaces.GetAddress(destinations[flow]), kPorts[flow]));
        source.SetConstantRate(DataRate(kDataRate), kPacketSize);
        source.SetAttribute("OnTime", StringValue("ns3::ConstantRandomVariable[Constant=1]"));
        source.SetAttribute("OffTime", StringValue("ns3::ConstantRandomVariable[Constant=0]"));
        ApplicationContainer sourceApp = source.Install(nodes.Get(flow));
        sourceApp.Start(Seconds(kAppStartS));
        sourceApp.Stop(Seconds(kAppStopS));
    }

    std::ofstream mobilityOut(outDir / "mobility.csv");
    if (!mobilityOut)
    {
        Fail("cannot write mobility.csv");
    }
    mobilityOut << "node_id,time_s,x_m,y_m,z_m\n";
    mobilityOut << std::setprecision(12);
    const uint32_t lastSecond = static_cast<uint32_t>(kSimStopS);
    for (uint32_t second = 0; second <= lastSecond; ++second)
    {
        Simulator::Schedule(Seconds(second), &SampleMobility, &mobilityOut, nodes, second);
    }

    FlowMonitorHelper flowmonHelper;
    Ptr<FlowMonitor> flowmon = flowmonHelper.InstallAll();

    std::unique_ptr<AnimationInterface> anim;
    if (opt.enableAnimation)
    {
        anim = std::make_unique<AnimationInterface>((outDir / "animation.xml").string());
        anim->SetMobilityPollInterval(Seconds(1.0));
        anim->EnablePacketMetadata(true);
        // Three conversations, one color each. Relays stay gray.
        // S1 green talks to D1, S2 blue talks to D2, S3 orange talks to D3.
        const uint8_t flowRgb[3][3] = {{0, 158, 115}, {0, 114, 178}, {230, 159, 0}};
        for (uint32_t i = 0; i < nodes.GetN(); ++i)
        {
            std::string label = "relay " + std::to_string(i);
            uint8_t red = 120;
            uint8_t green = 120;
            uint8_t blue = 120;
            double size = 6.0;
            if (i < 3)
            {
                label = "S" + std::to_string(i + 1) + " sends";
                red = flowRgb[i][0];
                green = flowRgb[i][1];
                blue = flowRgb[i][2];
                size = 14.0;
            }
            for (uint32_t flow = 0; flow < 3; ++flow)
            {
                if (i == destinations[flow])
                {
                    label = "D" + std::to_string(flow + 1) + " receives";
                    red = flowRgb[flow][0];
                    green = flowRgb[flow][1];
                    blue = flowRgb[flow][2];
                    size = 14.0;
                }
            }
            anim->UpdateNodeDescription(nodes.Get(i), label);
            anim->UpdateNodeColor(nodes.Get(i), red, green, blue);
            anim->UpdateNodeSize(nodes.Get(i), size, size);
        }
    }

    Simulator::Stop(Seconds(kSimStopS));
    Simulator::Run();

    flowmon->CheckForLostPackets();
    flowmon->SerializeToXmlFile((outDir / "flowmon.xml").string(), false, false);

    Ptr<Ipv4FlowClassifier> classifier =
        DynamicCast<Ipv4FlowClassifier>(flowmonHelper.GetClassifier());
    if (!classifier)
    {
        Fail("IPv4 flow classifier is missing");
    }

    std::ofstream flowsOut(outDir / "flows.csv");
    if (!flowsOut)
    {
        Fail("cannot write flows.csv");
    }
    flowsOut << std::setprecision(17);
    flowsOut << "flow_id,selected,protocol,source_address,destination_address,source_port,"
                "destination_port,tx_packets,rx_packets,tx_bytes,rx_bytes,delay_sum_s,"
                "lost_packets\n";

    FlowTotals totals;
    uint32_t matchedPorts[3] = {0, 0, 0};
    std::string warnings;
    const auto stats = flowmon->GetFlowStats();
    for (const auto& entry : stats)
    {
        const Ipv4FlowClassifier::FiveTuple tuple = classifier->FindFlow(entry.first);
        bool selected = false;
        int portIndex = -1;
        if (tuple.protocol == kUdpProtocol)
        {
            for (int i = 0; i < 3; ++i)
            {
                if (tuple.destinationPort == kPorts[i] &&
                    tuple.sourceAddress == interfaces.GetAddress(static_cast<uint32_t>(i)) &&
                    tuple.destinationAddress == interfaces.GetAddress(destinations[i]))
                {
                    selected = true;
                    portIndex = i;
                }
            }
        }
        flowsOut << entry.first << "," << (selected ? 1 : 0) << ","
                 << static_cast<uint32_t>(tuple.protocol) << "," << tuple.sourceAddress << ","
                 << tuple.destinationAddress << "," << tuple.sourcePort << ","
                 << tuple.destinationPort << "," << entry.second.txPackets << ","
                 << entry.second.rxPackets << "," << entry.second.txBytes << ","
                 << entry.second.rxBytes << "," << entry.second.delaySum.GetSeconds() << ","
                 << entry.second.lostPackets << "\n";
        if (!selected)
        {
            continue;
        }
        if (portIndex >= 0)
        {
            matchedPorts[portIndex] += 1;
        }
        totals.selectedFlows += 1;
        totals.txPackets += entry.second.txPackets;
        totals.rxPackets += entry.second.rxPackets;
        totals.txBytes += entry.second.txBytes;
        totals.rxBytes += entry.second.rxBytes;
        totals.delaySumS += entry.second.delaySum.GetSeconds();
        totals.lostPackets += entry.second.lostPackets;
        totals.jitterSumS += entry.second.jitterSum.GetSeconds();
        if (entry.second.txPackets > 0)
        {
            totals.flowsWithTx += 1;
        }
    }
    flowsOut.close();
    mobilityOut.flush();

    if (totals.txPackets < totals.rxPackets)
    {
        warnings += "rx_packets exceeds tx_packets; ";
    }
    for (int i = 0; i < 3; ++i)
    {
        if (matchedPorts[i] == 0)
        {
            warnings += "missing app flow on port " + std::to_string(kPorts[i]) + "; ";
        }
        else if (matchedPorts[i] > 1)
        {
            warnings += "duplicate app flow on port " + std::to_string(kPorts[i]) + "; ";
        }
    }

    std::string status = "PASS";
    if (totals.txPackets == 0 || totals.rxPackets == 0 || totals.flowsWithTx != 3 ||
        totals.selectedFlows != 3 || totals.txPackets < totals.rxPackets)
    {
        status = "INVALID";
    }
    const double throughput =
        (8.0 * static_cast<double>(totals.rxBytes)) / (kMeasurementS * 1000.0);
    if (!std::isfinite(throughput) || throughput < 0.0)
    {
        status = "INVALID";
        warnings += "throughput is not finite; ";
    }

    WriteSummary(summaryPath, opt, totals, status, warnings);
    WriteManifest(outDir / "manifest.json", opt, command, started, status, warnings);

    std::cout << "=== manet-aat metrics (UDP app flows only) ===\n";
    std::cout << "selected_flows: " << totals.selectedFlows << "\n";
    std::cout << "tx_packets: " << totals.txPackets << "\n";
    std::cout << "rx_packets: " << totals.rxPackets << "\n";
    std::cout << "tx_bytes: " << totals.txBytes << "\n";
    std::cout << "rx_bytes: " << totals.rxBytes << "\n";
    std::cout << "packet_loss_packets: ";
    if (totals.txPackets >= totals.rxPackets)
    {
        std::cout << (totals.txPackets - totals.rxPackets) << "\n";
    }
    else
    {
        std::cout << "undefined\n";
    }
    if (totals.txPackets > 0)
    {
        std::cout << "pdr_percent: "
                  << (100.0 * static_cast<double>(totals.rxPackets) /
                      static_cast<double>(totals.txPackets))
                  << "\n";
    }
    else
    {
        std::cout << "pdr_percent: undefined\n";
    }
    if (totals.rxPackets > 0)
    {
        std::cout << "avg_delay_ms: "
                  << (1000.0 * totals.delaySumS / static_cast<double>(totals.rxPackets)) << "\n";
    }
    else
    {
        std::cout << "avg_delay_ms: undefined\n";
    }
    std::cout << "throughput_kbps: " << throughput << "\n";
    std::cout << "flowmonitor_lost_packets_diagnostic: " << totals.lostPackets << "\n";
    std::cout << "status: " << status << "\n";
    if (!warnings.empty())
    {
        std::cout << "warnings: " << warnings << "\n";
    }

    anim.reset();
    Simulator::Destroy();
    return status == "PASS" ? 0 : 2;
}
