import { ImageResponse } from "next/og";

export const size = { width: 512, height: 512 };
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: 512,
          height: 512,
          background: "#d35322",
          borderRadius: 112,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 0,
        }}
      >
        {/* "A" small label */}
        <div
          style={{
            fontFamily: "serif",
            fontSize: 80,
            fontWeight: 400,
            color: "rgba(255,255,255,0.75)",
            letterSpacing: "0.3em",
            lineHeight: 1,
            marginBottom: -8,
          }}
        >
          A
        </div>
        {/* Thin rule */}
        <div
          style={{
            width: 200,
            height: 2,
            background: "rgba(255,255,255,0.35)",
            borderRadius: 1,
            margin: "12px 0",
          }}
        />
        {/* "R" main letter */}
        <div
          style={{
            fontFamily: "Georgia, serif",
            fontSize: 240,
            fontWeight: 400,
            color: "#ffffff",
            lineHeight: 1,
            marginTop: -8,
          }}
        >
          R
        </div>
      </div>
    ),
    { width: 512, height: 512 }
  );
}
