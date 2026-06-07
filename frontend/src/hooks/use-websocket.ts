"use client";

import { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";
import { useNotificationStore } from "@/stores/notification-store";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const addNotification = useNotificationStore((s) => s.addNotification);

  useEffect(() => {
    // Dynamic import for socket.io-client (client-side only)
    let socket: any = null;

    const connect = async () => {
      try {
        const { io } = await import("socket.io-client");
        socket = io(WS_URL, {
          transports: ["websocket", "polling"],
          autoConnect: true,
        });

        socket.on("connect", () => {
          setIsConnected(true);
          console.log("WebSocket connected");
        });

        socket.on("disconnect", () => {
          setIsConnected(false);
          console.log("WebSocket disconnected");
        });

        socket.on("notification:new", (data: any) => {
          addNotification({
            id: crypto.randomUUID(),
            user_id: data.user_id || "",
            type: data.type || "system",
            title: data.title || "Notification",
            message: data.message || "",
            read: false,
            data: data.data || {},
            created_at: new Date().toISOString(),
          });
          toast(data.title, { description: data.message });
        });

        socket.on("execution:completed", (data: any) => {
          toast.success("Workflow completed", {
            description: `Execution ${data.execution_id?.slice(0, 8)} finished`,
          });
        });

        socket.on("execution:failed", (data: any) => {
          toast.error("Workflow failed", {
            description: data.error || "An error occurred",
          });
        });
      } catch (err) {
        console.error("WebSocket connection error:", err);
      }
    };

    connect();

    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, [addNotification]);

  const subscribe = useCallback((channel: string) => {
    // Implementation depends on socket setup
    console.log(`Subscribing to: ${channel}`);
  }, []);

  return { isConnected, subscribe };
}
