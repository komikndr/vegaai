import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

const StatusCard = () => {
  const { dag_processor, metadatabase, scheduler, triggerer } = props;

  const renderItem = (title, item) => (
    <div className="mb-4">
      <h3 className="font-medium">{title}</h3>
      <p>Status: {item.status || "N/A"}</p>
      <p>
        Heartbeat:{" "}
        {item.latest_dag_processor_heartbeat ||
          item.latest_scheduler_heartbeat ||
          item.latest_triggerer_heartbeat ||
          "N/A"}
      </p>
    </div>
  );

  return (
    <Card className="max-w-md mx-auto mt-4">
      <CardHeader>
        <CardTitle>Airflow Status</CardTitle>
      </CardHeader>
      <CardContent>
        {renderItem("DAG Processor", dag_processor)}
        {renderItem("Metadata Database", metadatabase)}
        {renderItem("Scheduler", scheduler)}
        {renderItem("Triggerer", triggerer)}
      </CardContent>
    </Card>
  );
};

export default StatusCard;
