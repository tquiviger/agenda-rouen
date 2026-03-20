import { ImageResponse } from "next/og";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: 180,
          height: 180,
          background: "#d35322",
          borderRadius: 40,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 0,
        }}
      >
        <div
          style={{
            fontFamily: "serif",
            fontSize: 28,
            fontWeight: 400,
            color: "rgba(255,255,255,0.75)",
            letterSpacing: "0.3em",
            lineHeight: 1,
            marginBottom: -4,
          }}
        >
          A
        </div>
        <div
          style={{
            width: 70,
            height: 1,
            background: "rgba(255,255,255,0.35)",
            borderRadius: 1,
            margin: "6px 0",
          }}
        />
        <div
          style={{
            fontFamily: "Georgia, serif",
            fontSize: 86,
            fontWeight: 400,
            color: "#ffffff",
            lineHeight: 1,
            marginTop: -4,
          }}
        >
          R
        </div>
      </div>
    ),
    { width: 180, height: 180 }
  );
}
