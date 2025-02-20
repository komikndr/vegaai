import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const ClusterHealthCard = () => {
  const statusColors = {
    green: "text-green-500",
    yellow: "text-yellow-500",
    red: "text-red-500",
  };

  const renderItem = (label, value, isStatus = false) => (
    <div className="mb-4">
      <h3 className="font-medium">{label}</h3>
      <p className={isStatus ? statusColors[value] || "text-gray-500" : ""}>
        {value}
      </p>
    </div>
  );

  return (
    <Card className="max-w-md mx-auto mt-4">
      <CardHeader>
        <CardTitle>OpenSearch Cluster Health</CardTitle>
      </CardHeader>
      <CardContent>
        {renderItem("Cluster Name", props.cluster_name)}
        {renderItem("Status", props.status, true)}
        {renderItem("Number of Nodes", props.number_of_nodes)}
        {renderItem("Active Shards", props.active_shards)}
        {renderItem("Unassigned Shards", props.unassigned_shards)}
      </CardContent>
      <CardFooter>
        <Button
          onClick={() => window.open("https://10.10.5.11:7070", "_blank")}
        >
          Show more details in OpenSearch
        </Button>
      </CardFooter>
    </Card>
  );
};

export default ClusterHealthCard;
