package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/frontend/genproto"
	"github.com/pkg/errors"
)

type compareMoney struct {
	CurrencyCode string `json:"currency_code"`
	Units        int64  `json:"units"`
	Nanos        int32  `json:"nanos"`
}

type compareProduct struct {
	ID          string       `json:"id"`
	Name        string       `json:"name"`
	Description string       `json:"description"`
	Price       compareMoney `json:"price"`
}

type compareResponse struct {
	Products []compareProduct `json:"products"`
	Summary  string           `json:"summary"`
}

type compareRequest struct {
	ProductIDs []string `json:"product_ids"`
}

type compareErrorResponse struct {
	Error string `json:"error"`
}

func (fe *frontendServer) compareProducts(ctx context.Context, productIDs []string) (*compareResponse, error) {
	if fe.compareSvcAddr == "" {
		return nil, errors.New("compare service address not configured")
	}

	payload := compareRequest{ProductIDs: productIDs}
	body, err := json.Marshal(payload)
	if err != nil {
		return nil, errors.Wrap(err, "failed to marshal compare request")
	}

	compareURL := fmt.Sprintf("http://%s/compare", fe.compareSvcAddr)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, compareURL, bytes.NewReader(body))
	if err != nil {
		return nil, errors.Wrap(err, "failed to build compare request")
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, errors.Wrap(err, "compare service request failed")
	}
	defer resp.Body.Close()

	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, errors.Wrap(err, "failed to read compare response")
	}

	if resp.StatusCode != http.StatusOK {
		var compareErr compareErrorResponse
		if err := json.Unmarshal(responseBody, &compareErr); err == nil && compareErr.Error != "" {
			return nil, errors.Errorf("compare service error: %s", compareErr.Error)
		}
		return nil, errors.Errorf("compare service returned status %d", resp.StatusCode)
	}

	var compareResp compareResponse
	if err := json.Unmarshal(responseBody, &compareResp); err != nil {
		return nil, errors.Wrap(err, "failed to decode compare response")
	}

	return &compareResp, nil
}

func toMoneyView(m compareMoney) *pb.Money {
	return &pb.Money{
		CurrencyCode: m.CurrencyCode,
		Units:        m.Units,
		Nanos:        m.Nanos,
	}
}
